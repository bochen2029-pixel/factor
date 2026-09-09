// probe.cpp -- FACTOR M0 sandbox child probe.
// Runs four tests and prints one line per test: TEST <NAME> <PASS|FAIL|INFO> ...
// Built for MSVC x64. Link: ws2_32.lib advapi32.lib.
//
// PASS/FAIL convention is written from the *sandbox* point of view:
//   SOCKET PASS = egress was denied (refused/timed-out/blocked/socket-create-failed)
//   AFD    PASS = the raw transport device could not be opened
//   PIPE   PASS = the granted pipe worked AND the ungranted default pipe was denied
//   CUDA   PASS = nvcuda loaded, cuInit + device query + 64 MiB round-trip all succeeded
// The launcher runs this both inside and outside the container; the report compares them.

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "advapi32.lib")

static void line(const char* s) { fputs(s, stdout); fputc('\n', stdout); fflush(stdout); }

// ----------------------------------------------------------------------------
// (a) SOCKET
// ----------------------------------------------------------------------------
static const char* wsaLabel(int e) {
    switch (e) {
        case 0: return "ok";
        case WSAECONNREFUSED: return "refused";       // 10061
        case WSAETIMEDOUT:    return "timed-out";      // 10060
        case WSAEACCES:       return "blocked-EACCES"; // 10013  (WFP)
        case WSAENETUNREACH:  return "net-unreach";    // 10051
        case WSAEHOSTUNREACH: return "host-unreach";   // 10065
        case WSAENETDOWN:     return "net-down";        // 10050
        case WSAEAFNOSUPPORT: return "af-nosupport";   // 10047
        case WSAEPROVIDERFAILEDINIT: return "provider-init-fail"; // 10106
        default: return "other";
    }
}

// Returns 0 if the TCP connect SUCCEEDED (egress leaked); otherwise a WSA code.
// On success *connected=1.
static int tryConnect(const char* ip, unsigned short port, int* connected, int* outCode) {
    *connected = 0; *outCode = 0;
    SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) { *outCode = WSAGetLastError(); return *outCode ? *outCode : -1; }
    u_long nb = 1; ioctlsocket(s, FIONBIO, &nb);
    sockaddr_in a; memset(&a, 0, sizeof a);
    a.sin_family = AF_INET; a.sin_port = htons(port);
    inet_pton(AF_INET, ip, &a.sin_addr);
    int r = connect(s, (sockaddr*)&a, sizeof a);
    if (r == 0) { *connected = 1; closesocket(s); return 0; }
    int e = WSAGetLastError();
    if (e == WSAEWOULDBLOCK) {
        fd_set wr, ex; FD_ZERO(&wr); FD_ZERO(&ex); FD_SET(s, &wr); FD_SET(s, &ex);
        timeval tv; tv.tv_sec = 3; tv.tv_usec = 0;
        int sr = select(0, NULL, &wr, &ex, &tv);
        if (sr == 0) { *outCode = WSAETIMEDOUT; closesocket(s); return WSAETIMEDOUT; }
        int so = 0; int l = sizeof so;
        getsockopt(s, SOL_SOCKET, SO_ERROR, (char*)&so, &l);
        if (so == 0 && FD_ISSET(s, &wr)) { *connected = 1; closesocket(s); return 0; }
        *outCode = so ? so : WSAECONNREFUSED; closesocket(s); return *outCode;
    }
    *outCode = e; closesocket(s); return e;
}

static void testSocket(unsigned short loopPort) {
    WSADATA wsa;
    int ws = WSAStartup(MAKEWORD(2, 2), &wsa);
    if (ws != 0) {
        char b[256];
        _snprintf_s(b, sizeof b, _TRUNCATE,
            "TEST SOCKET PASS wsastartup_failed=%d note=\"WSAStartup itself refused\"", ws);
        line(b); return;
    }
    int lc = 0, lcode = 0; tryConnect("127.0.0.1", 9, &lc, &lcode);
    int ic = 0, icode = 0; tryConnect("1.1.1.1", 80, &ic, &icode);
    // Positive loopback control: a real listener the launcher is running.
    int pc = 0, pcode = 0;
    if (loopPort) tryConnect("127.0.0.1", loopPort, &pc, &pcode);
    WSACleanup();
    // From the sandbox POV, PASS = no real egress: internet blocked AND the live
    // loopback listener unreachable. (:9 discard has nothing listening, so it is
    // informational only.)
    const char* verdict = (!ic && !pc) ? "PASS" : "FAIL";
    char b[640];
    _snprintf_s(b, sizeof b, _TRUNCATE,
        "TEST SOCKET %s loopback_127.0.0.1:9=%s(%d) internet_1.1.1.1:80=%s(%d) loopback_live_127.0.0.1:%u=%s(%d) egress_leaked=%s",
        verdict, wsaLabel(lc ? 0 : lcode), lc ? 0 : lcode,
        wsaLabel(ic ? 0 : icode), ic ? 0 : icode,
        (unsigned)loopPort, pc ? "connected" : wsaLabel(pcode), pc ? 0 : pcode,
        (ic || pc) ? "YES" : "no");
    line(b);
}

// ----------------------------------------------------------------------------
// (b) AFD  --  NtCreateFile on \Device\Afd
// ----------------------------------------------------------------------------
typedef LONG NTSTATUS;
typedef struct _UNICODE_STRING { USHORT Length; USHORT MaximumLength; PWSTR Buffer; } UNICODE_STRING;
typedef struct _OBJECT_ATTRIBUTES {
    ULONG Length; HANDLE RootDirectory; UNICODE_STRING* ObjectName;
    ULONG Attributes; PVOID SecurityDescriptor; PVOID SecurityQualityOfService;
} OBJECT_ATTRIBUTES;
typedef struct _IO_STATUS_BLOCK { union { NTSTATUS Status; PVOID Pointer; } u; ULONG_PTR Information; } IO_STATUS_BLOCK;

typedef NTSTATUS (NTAPI *PFN_NtCreateFile)(PHANDLE, ACCESS_MASK, OBJECT_ATTRIBUTES*, IO_STATUS_BLOCK*,
    PLARGE_INTEGER, ULONG, ULONG, ULONG, ULONG, PVOID, ULONG);

#define OBJ_CASE_INSENSITIVE 0x00000040L
#define FILE_OPEN 0x00000001

static NTSTATUS openDevice(PFN_NtCreateFile fn, const wchar_t* path, HANDLE* ph) {
    *ph = NULL;
    UNICODE_STRING us;
    size_t len = wcslen(path) * sizeof(wchar_t);
    us.Buffer = (PWSTR)path; us.Length = (USHORT)len; us.MaximumLength = (USHORT)(len + sizeof(wchar_t));
    OBJECT_ATTRIBUTES oa; memset(&oa, 0, sizeof oa);
    oa.Length = sizeof oa; oa.ObjectName = &us; oa.Attributes = OBJ_CASE_INSENSITIVE;
    IO_STATUS_BLOCK iosb; memset(&iosb, 0, sizeof iosb);
    return fn(ph, GENERIC_READ | GENERIC_WRITE | SYNCHRONIZE, &oa, &iosb, NULL, 0,
              FILE_SHARE_READ | FILE_SHARE_WRITE, FILE_OPEN, 0, NULL, 0);
}

static void testAfd() {
    HMODULE nt = GetModuleHandleW(L"ntdll.dll");
    PFN_NtCreateFile fn = nt ? (PFN_NtCreateFile)GetProcAddress(nt, "NtCreateFile") : NULL;
    if (!fn) { line("TEST AFD INFO note=\"NtCreateFile unresolved\""); return; }

    HANDLE h1 = NULL, h2 = NULL;
    NTSTATUS s1 = openDevice(fn, L"\\Device\\Afd\\Endpoint", &h1);
    if (h1) CloseHandle(h1);
    NTSTATUS s2 = openDevice(fn, L"\\Device\\Afd", &h2);
    if (h2) CloseHandle(h2);

    // NT_SUCCESS: STATUS >= 0. STATUS_ACCESS_DENIED = 0xC0000022.
    bool opened = (s1 >= 0) || (s2 >= 0);
    const char* verdict = opened ? "FAIL" : "PASS"; // PASS = device could NOT be opened
    char b[320];
    _snprintf_s(b, sizeof b, _TRUNCATE,
        "TEST AFD %s afd_endpoint_status=0x%08lX afd_raw_status=0x%08lX openable=%s",
        verdict, (unsigned long)s1, (unsigned long)s2, opened ? "YES" : "no");
    line(b);
}

// ----------------------------------------------------------------------------
// (c) PIPE
// ----------------------------------------------------------------------------
static bool openWriteReadPipe(const wchar_t* name, DWORD* err, char* echo, size_t echoSz) {
    *err = 0; echo[0] = 0;
    HANDLE h = CreateFileW(name, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING,
                           SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION, NULL);
    if (h == INVALID_HANDLE_VALUE) { *err = GetLastError(); return false; }
    const char* msg = "FACTOR-PROBE-PING";
    DWORD wr = 0; BOOL ok = WriteFile(h, msg, (DWORD)strlen(msg), &wr, NULL);
    if (!ok) { *err = GetLastError(); CloseHandle(h); return false; }
    DWORD rd = 0; char buf[256]; memset(buf, 0, sizeof buf);
    ok = ReadFile(h, buf, sizeof buf - 1, &rd, NULL);
    if (!ok) { *err = GetLastError(); CloseHandle(h); return false; }
    _snprintf_s(echo, echoSz, _TRUNCATE, "%s", buf);
    CloseHandle(h);
    return true;
}

static void testPipe(const wchar_t* securePipe, const wchar_t* defaultPipe) {
    if (!securePipe || !securePipe[0]) { line("TEST PIPE INFO note=\"no pipe names passed\""); return; }
    DWORD e1 = 0; char echo[256];
    bool ok1 = openWriteReadPipe(securePipe, &e1, echo, sizeof echo);
    bool echoOk = ok1 && strcmp(echo, "FACTOR-PROBE-PING") == 0;

    bool triedDefault = (defaultPipe && defaultPipe[0]);
    DWORD e2 = 0; char echo2[256]; bool ok2 = false;
    if (triedDefault) ok2 = openWriteReadPipe(defaultPipe, &e2, echo2, sizeof echo2);

    // PASS = granted pipe echoed AND default pipe was denied (or at least not usable).
    const char* verdict = (echoOk && (!triedDefault || !ok2)) ? "PASS" : "FAIL";
    char b[512];
    _snprintf_s(b, sizeof b, _TRUNCATE,
        "TEST PIPE %s secure=%s(err=%lu) secure_echo=\"%s\" default=%s(err=%lu)",
        verdict, echoOk ? "OK" : "FAIL", (unsigned long)e1, echoOk ? echo : "",
        triedDefault ? (ok2 ? "OPENED" : "denied") : "n/a", (unsigned long)e2);
    line(b);
}

// ----------------------------------------------------------------------------
// (d) CUDA  --  nvcuda.dll driver API round trip
// ----------------------------------------------------------------------------
#ifndef CUDAAPI
#define CUDAAPI __stdcall
#endif
typedef int CUresult;
typedef int CUdevice;
typedef void* CUcontext;
typedef unsigned long long CUdeviceptr;

typedef CUresult (CUDAAPI *PFN_cuInit)(unsigned int);
typedef CUresult (CUDAAPI *PFN_cuDeviceGetCount)(int*);
typedef CUresult (CUDAAPI *PFN_cuDeviceGet)(CUdevice*, int);
typedef CUresult (CUDAAPI *PFN_cuDeviceGetName)(char*, int, CUdevice);
typedef CUresult (CUDAAPI *PFN_cuCtxCreate)(CUcontext*, unsigned int, CUdevice);
typedef CUresult (CUDAAPI *PFN_cuCtxDestroy)(CUcontext);
typedef CUresult (CUDAAPI *PFN_cuMemAlloc)(CUdeviceptr*, size_t);
typedef CUresult (CUDAAPI *PFN_cuMemFree)(CUdeviceptr);
typedef CUresult (CUDAAPI *PFN_cuMemcpyHtoD)(CUdeviceptr, const void*, size_t);
typedef CUresult (CUDAAPI *PFN_cuMemcpyDtoH)(void*, CUdeviceptr, size_t);
typedef CUresult (CUDAAPI *PFN_cuGetErrorName)(CUresult, const char**);

static void testCuda() {
    char b[900];
    HMODULE cu = LoadLibraryW(L"nvcuda.dll");
    if (!cu) {
        DWORD e = GetLastError();
        _snprintf_s(b, sizeof b, _TRUNCATE,
            "TEST CUDA FAIL load_nvcuda=FAIL LoadLibrary_err=%lu note=\"nvcuda.dll could not load in this token\"",
            (unsigned long)e);
        line(b); return;
    }
    PFN_cuInit           cuInit    = (PFN_cuInit)GetProcAddress(cu, "cuInit");
    PFN_cuDeviceGetCount cuCount   = (PFN_cuDeviceGetCount)GetProcAddress(cu, "cuDeviceGetCount");
    PFN_cuDeviceGet      cuGet     = (PFN_cuDeviceGet)GetProcAddress(cu, "cuDeviceGet");
    PFN_cuDeviceGetName  cuName    = (PFN_cuDeviceGetName)GetProcAddress(cu, "cuDeviceGetName");
    PFN_cuCtxCreate      cuCtxNew  = (PFN_cuCtxCreate)GetProcAddress(cu, "cuCtxCreate_v2");
    PFN_cuCtxDestroy     cuCtxDel  = (PFN_cuCtxDestroy)GetProcAddress(cu, "cuCtxDestroy_v2");
    PFN_cuMemAlloc       cuAlloc   = (PFN_cuMemAlloc)GetProcAddress(cu, "cuMemAlloc_v2");
    PFN_cuMemFree        cuFree    = (PFN_cuMemFree)GetProcAddress(cu, "cuMemFree_v2");
    PFN_cuMemcpyHtoD     cuH2D     = (PFN_cuMemcpyHtoD)GetProcAddress(cu, "cuMemcpyHtoD_v2");
    PFN_cuMemcpyDtoH     cuD2H     = (PFN_cuMemcpyDtoH)GetProcAddress(cu, "cuMemcpyDtoH_v2");
    PFN_cuGetErrorName   cuErrName = (PFN_cuGetErrorName)GetProcAddress(cu, "cuGetErrorName");

    if (!cuInit || !cuCount || !cuGet || !cuName || !cuCtxNew || !cuCtxDel || !cuAlloc || !cuFree || !cuH2D || !cuD2H) {
        _snprintf_s(b, sizeof b, _TRUNCATE,
            "TEST CUDA FAIL load_nvcuda=OK note=\"driver API entry points missing\"");
        line(b); return;
    }

    CUresult rInit = cuInit(0);
    int count = -1; CUresult rCount = (rInit == 0) ? cuCount(&count) : rInit;
    CUdevice dev = 0; CUresult rGet = (rCount == 0 && count > 0) ? cuGet(&dev, 0) : (CUresult)(-99);
    char devName[256]; memset(devName, 0, sizeof devName);
    CUresult rName = (rGet == 0) ? cuName(devName, (int)sizeof devName, dev) : (CUresult)(-99);
    CUcontext ctx = NULL; CUresult rCtx = (rGet == 0) ? cuCtxNew(&ctx, 0, dev) : (CUresult)(-99);

    const size_t BYTES = 64ull * 1024 * 1024; // 64 MiB
    CUdeviceptr dptr = 0; CUresult rAlloc = (rCtx == 0) ? cuAlloc(&dptr, BYTES) : (CUresult)(-99);

    CUresult rH2D = (CUresult)(-99), rD2H = (CUresult)(-99);
    int match = -1;
    if (rAlloc == 0) {
        unsigned char* src = (unsigned char*)malloc(BYTES);
        unsigned char* dst = (unsigned char*)malloc(BYTES);
        if (src && dst) {
            for (size_t i = 0; i < BYTES; i++) src[i] = (unsigned char)((i * 2654435761u) >> 24);
            rH2D = cuH2D(dptr, src, BYTES);
            if (rH2D == 0) {
                memset(dst, 0, BYTES);
                rD2H = cuD2H(dst, dptr, BYTES);
                if (rD2H == 0) match = (memcmp(src, dst, BYTES) == 0) ? 1 : 0;
            }
        }
        free(src); free(dst);
        cuFree(dptr);
    }
    if (ctx) cuCtxDel(ctx);

    const char* errN = "?";
    if (cuErrName && rInit != 0) cuErrName(rInit, &errN);

    bool pass = (rInit == 0 && rCount == 0 && count > 0 && rCtx == 0 && rAlloc == 0 &&
                 rH2D == 0 && rD2H == 0 && match == 1);
    _snprintf_s(b, sizeof b, _TRUNCATE,
        "TEST CUDA %s load_nvcuda=OK cuInit=%d(%s) count=%d dev0=\"%s\" cuCtxCreate=%d cuMemAlloc64MiB=%d HtoD=%d DtoH=%d roundtrip=%s",
        pass ? "PASS" : "FAIL", rInit, (rInit == 0 ? "CUDA_SUCCESS" : errN), count, devName,
        rCtx, rAlloc, rH2D, rD2H, (match == 1 ? "MATCH" : (match == 0 ? "MISMATCH" : "n/a")));
    line(b);
}

// ----------------------------------------------------------------------------
int wmain(int argc, wchar_t** argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    const wchar_t* securePipe = L"";
    const wchar_t* defaultPipe = L"";
    const wchar_t* tag = L"unknown";
    unsigned short loopPort = 0;
    for (int i = 1; i < argc; ++i) {
        if (!wcscmp(argv[i], L"--secure-pipe") && i + 1 < argc) securePipe = argv[++i];
        else if (!wcscmp(argv[i], L"--default-pipe") && i + 1 < argc) defaultPipe = argv[++i];
        else if (!wcscmp(argv[i], L"--tag") && i + 1 < argc) tag = argv[++i];
        else if (!wcscmp(argv[i], L"--loopback-port") && i + 1 < argc) loopPort = (unsigned short)_wtoi(argv[++i]);
    }
    char hb[256];
    _snprintf_s(hb, sizeof hb, _TRUNCATE, "PROBE-BEGIN tag=%ls pid=%lu", tag, GetCurrentProcessId());
    line(hb);
    testSocket(loopPort);
    testAfd();
    testPipe(securePipe, defaultPipe);
    testCuda();
    line("PROBE-END");
    return 0;
}
