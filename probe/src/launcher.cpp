// launcher.cpp -- FACTOR M0 sandbox launcher.
// Creates the AppContainer profile "FACTOR-probe" with ZERO capabilities, derives the
// package SID, and launches a child either inside that container (with
// PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES + CHILD_PROCESS_RESTRICTED) or outside it
// as the control. Serves two named pipes (one granting the package SID, one default).
//
// Modes:
//   launcher.exe ensure                         -- create/derive profile, print SID
//   launcher.exe probe-outside                  -- run probe.exe outside the container
//   launcher.exe probe-inside                   -- run probe.exe inside the container
//   launcher.exe llama-outside <model> <exe>    -- run llama bench outside
//   launcher.exe llama-inside  <model> <exe>    -- run llama bench inside
//   launcher.exe cleanup                        -- revoke ACEs, DeleteAppContainerProfile
//
// Built for MSVC x64 (/MT). Link: userenv.lib advapi32.lib.

#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0A00
#endif
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <userenv.h>
#include <sddl.h>
#include <aclapi.h>
#include <stdio.h>
#include <string.h>

#pragma comment(lib, "userenv.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "ws2_32.lib")

#ifndef PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES
#define PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES \
    ProcThreadAttributeValue(9, FALSE, TRUE, FALSE)
#endif
#ifndef PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY
#define PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY \
    ProcThreadAttributeValue(14, FALSE, TRUE, FALSE)
#endif
#ifndef PROCESS_CREATION_CHILD_PROCESS_RESTRICTED
#define PROCESS_CREATION_CHILD_PROCESS_RESTRICTED 0x00000001
#endif

static const wchar_t* AC_NAME  = L"FACTOR-probe";
static const wchar_t* AC_DISP  = L"FACTOR M0 sandbox probe";
static const wchar_t* AC_DESC  = L"Zero-capability AppContainer for the FACTOR M0 sandbox measurement";
static const wchar_t* PIPE_SECURE  = L"\\\\.\\pipe\\FACTOR-probe-secure";
static const wchar_t* PIPE_DEFAULT = L"\\\\.\\pipe\\FACTOR-probe-default";

static const wchar_t* PATH_BIN   = L"C:\\FACTOR\\probe\\bin";
static const wchar_t* PATH_OUT   = L"C:\\FACTOR\\probe\\out";

static PSID     g_acSid = NULL;
static wchar_t  g_sidStr[256] = L"";
static HANDLE   g_hStop = NULL;

// ----------------------------------------------------------------------------
static bool ensureProfile(bool announce) {
    HRESULT hr = CreateAppContainerProfile(AC_NAME, AC_DISP, AC_DESC, NULL, 0, &g_acSid);
    if (hr == HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)) {
        hr = DeriveAppContainerSidFromAppContainerName(AC_NAME, &g_acSid);
    }
    if (FAILED(hr)) {
        wprintf(L"ERROR CreateAppContainerProfile/Derive failed hr=0x%08lX\n", (unsigned long)hr);
        return false;
    }
    LPWSTR s = NULL;
    if (ConvertSidToStringSidW(g_acSid, &s)) {
        wcsncpy_s(g_sidStr, s, _TRUNCATE);
        LocalFree(s);
    }
    if (announce) wprintf(L"PACKAGE-SID: %s\n", g_sidStr);
    return true;
}

// Grant an ACE on a path for the AppContainer package SID.
static bool grantSid(const wchar_t* path, DWORD accessPerms, bool inherit) {
    PACL oldAcl = NULL, newAcl = NULL; PSECURITY_DESCRIPTOR sd = NULL;
    DWORD r = GetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT, DACL_SECURITY_INFORMATION,
                                    NULL, NULL, &oldAcl, NULL, &sd);
    if (r != ERROR_SUCCESS) { wprintf(L"  grant: GetNamedSecurityInfo(%s) err=%lu\n", path, r); return false; }
    EXPLICIT_ACCESSW ea; memset(&ea, 0, sizeof ea);
    ea.grfAccessPermissions = accessPerms;
    ea.grfAccessMode = GRANT_ACCESS;
    ea.grfInheritance = inherit ? (CONTAINER_INHERIT_ACE | OBJECT_INHERIT_ACE) : NO_INHERITANCE;
    ea.Trustee.TrusteeForm = TRUSTEE_IS_SID;
    ea.Trustee.TrusteeType = TRUSTEE_IS_UNKNOWN;
    ea.Trustee.ptstrName = (LPWSTR)g_acSid;
    r = SetEntriesInAclW(1, &ea, oldAcl, &newAcl);
    if (r != ERROR_SUCCESS) { wprintf(L"  grant: SetEntriesInAcl(%s) err=%lu\n", path, r); LocalFree(sd); return false; }
    r = SetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT, DACL_SECURITY_INFORMATION,
                              NULL, NULL, newAcl, NULL);
    if (newAcl) LocalFree(newAcl);
    if (sd) LocalFree(sd);
    if (r != ERROR_SUCCESS) { wprintf(L"  grant: SetNamedSecurityInfo(%s) err=%lu\n", path, r); return false; }
    wprintf(L"  granted 0x%08lX on %s (inherit=%d)\n", accessPerms, path, inherit ? 1 : 0);
    return true;
}

static void revokeSid(const wchar_t* path) {
    PACL oldAcl = NULL, newAcl = NULL; PSECURITY_DESCRIPTOR sd = NULL;
    DWORD r = GetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT, DACL_SECURITY_INFORMATION,
                                    NULL, NULL, &oldAcl, NULL, &sd);
    if (r != ERROR_SUCCESS) return;
    EXPLICIT_ACCESSW ea; memset(&ea, 0, sizeof ea);
    ea.grfAccessPermissions = 0;
    ea.grfAccessMode = REVOKE_ACCESS;
    ea.grfInheritance = NO_INHERITANCE;
    ea.Trustee.TrusteeForm = TRUSTEE_IS_SID;
    ea.Trustee.TrusteeType = TRUSTEE_IS_UNKNOWN;
    ea.Trustee.ptstrName = (LPWSTR)g_acSid;
    if (SetEntriesInAclW(1, &ea, oldAcl, &newAcl) == ERROR_SUCCESS) {
        SetNamedSecurityInfoW((LPWSTR)path, SE_FILE_OBJECT, DACL_SECURITY_INFORMATION,
                              NULL, NULL, newAcl, NULL);
        wprintf(L"  revoked package-SID ACE on %s\n", path);
    }
    if (newAcl) LocalFree(newAcl);
    if (sd) LocalFree(sd);
}

// ----------------------------------------------------------------------------
// Pipe server
struct PipeSrv { HANDLE hPipe; HANDLE hEvent; const wchar_t* tag; };

static HANDLE makePipe(const wchar_t* name, bool secure) {
    SECURITY_ATTRIBUTES sa; SECURITY_ATTRIBUTES* psa = NULL; PSECURITY_DESCRIPTOR sd = NULL;
    if (secure) {
        wchar_t sddl[600];
        // canonical order: deny ACEs first, then allow. Deny NETWORK (NU) and ANONYMOUS (AN).
        // Grant OWNER (OW) and SYSTEM (SY) full, and the AppContainer package SID read+write.
        _snwprintf_s(sddl, _TRUNCATE,
            L"D:P(D;;GA;;;NU)(D;;GA;;;AN)(A;;GA;;;OW)(A;;GA;;;SY)(A;;GRGW;;;%s)", g_sidStr);
        if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, SDDL_REVISION_1, &sd, NULL)) {
            wprintf(L"  makePipe: SDDL convert failed err=%lu\n", GetLastError());
            return INVALID_HANDLE_VALUE;
        }
        memset(&sa, 0, sizeof sa); sa.nLength = sizeof sa; sa.lpSecurityDescriptor = sd; sa.bInheritHandle = FALSE;
        psa = &sa;
    }
    DWORD openMode = PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED;
    if (secure) openMode |= FILE_FLAG_FIRST_PIPE_INSTANCE;
    DWORD pipeMode = PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS;
    HANDLE h = CreateNamedPipeW(name, openMode, pipeMode, 1, 4096, 4096, 0, psa);
    if (sd) LocalFree(sd);
    if (h == INVALID_HANDLE_VALUE)
        wprintf(L"  makePipe(%s secure=%d) failed err=%lu\n", name, secure ? 1 : 0, GetLastError());
    return h;
}

static DWORD WINAPI pipeThread(LPVOID p) {
    PipeSrv* ps = (PipeSrv*)p;
    OVERLAPPED ov; memset(&ov, 0, sizeof ov); ov.hEvent = ps->hEvent;
    BOOL ok = ConnectNamedPipe(ps->hPipe, &ov);
    DWORD err = GetLastError();
    if (!ok && err == ERROR_IO_PENDING) {
        HANDLE hs[2] = { ov.hEvent, g_hStop };
        DWORD w = WaitForMultipleObjects(2, hs, FALSE, INFINITE);
        if (w != WAIT_OBJECT_0) { CancelIoEx(ps->hPipe, &ov); return 0; }
    } else if (!ok && err != ERROR_PIPE_CONNECTED) {
        return 0;
    }
    ULONG clientPid = 0; GetNamedPipeClientProcessId(ps->hPipe, &clientPid);
    wprintf(L"  [pipe %s] client connected pid=%lu\n", ps->tag, clientPid);
    for (;;) {
        char buf[4096]; DWORD n = 0;
        ResetEvent(ov.hEvent);
        OVERLAPPED ro; memset(&ro, 0, sizeof ro); ro.hEvent = ov.hEvent;
        BOOL rok = ReadFile(ps->hPipe, buf, sizeof buf, &n, &ro);
        if (!rok) {
            DWORD re = GetLastError();
            if (re == ERROR_IO_PENDING) {
                HANDLE hs[2] = { ov.hEvent, g_hStop };
                DWORD w = WaitForMultipleObjects(2, hs, FALSE, INFINITE);
                if (w != WAIT_OBJECT_0) { CancelIoEx(ps->hPipe, &ro); break; }
                if (!GetOverlappedResult(ps->hPipe, &ro, &n, FALSE)) break;
            } else break;
        }
        if (n == 0) break;
        ResetEvent(ov.hEvent);
        OVERLAPPED wo; memset(&wo, 0, sizeof wo); wo.hEvent = ov.hEvent; DWORD wn = 0;
        BOOL wok = WriteFile(ps->hPipe, buf, n, &wn, &wo);
        if (!wok) {
            DWORD we = GetLastError();
            if (we == ERROR_IO_PENDING) { WaitForSingleObject(ov.hEvent, INFINITE); GetOverlappedResult(ps->hPipe, &wo, &wn, FALSE); }
            else break;
        }
        FlushFileBuffers(ps->hPipe);
    }
    DisconnectNamedPipe(ps->hPipe);
    return 0;
}

// ----------------------------------------------------------------------------
static HANDLE openInheritableFile(const wchar_t* path, bool write) {
    SECURITY_ATTRIBUTES sa; memset(&sa, 0, sizeof sa);
    sa.nLength = sizeof sa; sa.bInheritHandle = TRUE;
    if (write)
        return CreateFileW(path, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, &sa,
                           CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    return CreateFileW(path, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, &sa,
                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
}

// Launch a child, optionally inside the AppContainer. Returns exit code, or -1 on spawn fail.
static int launchChild(const wchar_t* exe, wchar_t* cmdline, const wchar_t* cwd,
                       const wchar_t* outFile, bool inside, DWORD timeoutMs) {
    HANDLE hOut = openInheritableFile(outFile, true);
    if (hOut == INVALID_HANDLE_VALUE) { wprintf(L"ERROR cannot open out file %s err=%lu\n", outFile, GetLastError()); return -1; }
    HANDLE hIn = openInheritableFile(L"NUL", false);

    STARTUPINFOEXW si; memset(&si, 0, sizeof si);
    si.StartupInfo.cb = sizeof si;
    si.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
    si.StartupInfo.hStdOutput = hOut;
    si.StartupInfo.hStdError  = hOut;
    si.StartupInfo.hStdInput  = hIn;

    LPPROC_THREAD_ATTRIBUTE_LIST atl = NULL;
    SECURITY_CAPABILITIES sc; memset(&sc, 0, sizeof sc);
    DWORD childPolicy = PROCESS_CREATION_CHILD_PROCESS_RESTRICTED;
    HANDLE inheritList[2] = { hOut, hIn };
    DWORD attrCount = inside ? 3 : 1;

    SIZE_T sz = 0;
    InitializeProcThreadAttributeList(NULL, attrCount, 0, &sz);
    atl = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, sz);
    if (!InitializeProcThreadAttributeList(atl, attrCount, 0, &sz)) {
        wprintf(L"ERROR InitializeProcThreadAttributeList err=%lu\n", GetLastError()); return -1;
    }
    if (inside) {
        sc.AppContainerSid = g_acSid; sc.Capabilities = NULL; sc.CapabilityCount = 0;
        if (!UpdateProcThreadAttribute(atl, 0, PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES, &sc, sizeof sc, NULL, NULL))
            wprintf(L"ERROR Update SECURITY_CAPABILITIES err=%lu\n", GetLastError());
        if (!UpdateProcThreadAttribute(atl, 0, PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY, &childPolicy, sizeof childPolicy, NULL, NULL))
            wprintf(L"ERROR Update CHILD_PROCESS_POLICY err=%lu\n", GetLastError());
    }
    UpdateProcThreadAttribute(atl, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST, inheritList, 2 * sizeof(HANDLE), NULL, NULL);
    si.lpAttributeList = atl;

    PROCESS_INFORMATION pi; memset(&pi, 0, sizeof pi);
    BOOL ok = CreateProcessW(exe, cmdline, NULL, NULL, TRUE,
                             EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT,
                             NULL, cwd, &si.StartupInfo, &pi);
    int rc = -1;
    if (!ok) {
        wprintf(L"ERROR CreateProcess(%s) err=%lu\n", exe, GetLastError());
    } else {
        wprintf(L"  child launched pid=%lu inside=%d\n", pi.dwProcessId, inside ? 1 : 0);
        DWORD w = WaitForSingleObject(pi.hProcess, timeoutMs);
        if (w == WAIT_TIMEOUT) {
            wprintf(L"  child TIMED OUT after %lu ms; terminating\n", timeoutMs);
            TerminateProcess(pi.hProcess, 258);
            WaitForSingleObject(pi.hProcess, 5000);
            rc = 258;
        } else {
            DWORD ec = 0; GetExitCodeProcess(pi.hProcess, &ec); rc = (int)ec;
            wprintf(L"  child exit code=%d\n", rc);
        }
        CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    }
    DeleteProcThreadAttributeList(atl);
    HeapFree(GetProcessHeap(), 0, atl);
    CloseHandle(hOut); CloseHandle(hIn);
    return rc;
}

// ----------------------------------------------------------------------------
// Positive loopback control: the launcher (outside the container) listens on
// 127.0.0.1:<port> so the probe can test whether a loopback connect is permitted
// from inside the container. If the container blocks loopback we see EACCES/timeout;
// if it does not, the connect succeeds against this listener.
static SOCKET g_listen = INVALID_SOCKET;
static DWORD WINAPI acceptLoop(LPVOID) {
    for (;;) {
        SOCKET c = accept(g_listen, NULL, NULL);
        if (c == INVALID_SOCKET) break;
        char b[64]; recv(c, b, sizeof b, 0);
        const char* pong = "LOOPBACK-OK";
        send(c, pong, (int)strlen(pong), 0);
        closesocket(c);
    }
    return 0;
}
static int startLoopbackListener() {
    WSADATA w; if (WSAStartup(MAKEWORD(2, 2), &w) != 0) return 0;
    g_listen = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (g_listen == INVALID_SOCKET) return 0;
    sockaddr_in a; memset(&a, 0, sizeof a); a.sin_family = AF_INET; a.sin_port = 0;
    inet_pton(AF_INET, "127.0.0.1", &a.sin_addr);
    if (bind(g_listen, (sockaddr*)&a, sizeof a) != 0) { closesocket(g_listen); g_listen = INVALID_SOCKET; return 0; }
    if (listen(g_listen, 4) != 0) { closesocket(g_listen); g_listen = INVALID_SOCKET; return 0; }
    int len = sizeof a; getsockname(g_listen, (sockaddr*)&a, &len);
    int port = ntohs(a.sin_port);
    CreateThread(NULL, 0, acceptLoop, NULL, 0, NULL);
    return port;
}

// ----------------------------------------------------------------------------
static int runProbe(bool inside) {
    if (!ensureProfile(true)) return 2;
    if (inside) {
        wprintf(L"ACL grants for probe-inside:\n");
        grantSid(PATH_BIN, GENERIC_READ | GENERIC_EXECUTE, true);
        grantSid(PATH_OUT, GENERIC_READ | GENERIC_WRITE | GENERIC_EXECUTE, true);
    }
    g_hStop = CreateEventW(NULL, TRUE, FALSE, NULL);
    HANDLE hSec = makePipe(PIPE_SECURE, true);
    HANDLE hDef = makePipe(PIPE_DEFAULT, false);
    PipeSrv sSec = { hSec, CreateEventW(NULL, TRUE, FALSE, NULL), L"secure" };
    PipeSrv sDef = { hDef, CreateEventW(NULL, TRUE, FALSE, NULL), L"default" };
    HANDLE tSec = (hSec != INVALID_HANDLE_VALUE) ? CreateThread(NULL, 0, pipeThread, &sSec, 0, NULL) : NULL;
    HANDLE tDef = (hDef != INVALID_HANDLE_VALUE) ? CreateThread(NULL, 0, pipeThread, &sDef, 0, NULL) : NULL;

    int loopPort = startLoopbackListener();
    wprintf(L"  loopback listener on 127.0.0.1:%d\n", loopPort);

    const wchar_t* tag = inside ? L"inside" : L"outside";
    const wchar_t* outFile = inside ? L"C:\\FACTOR\\probe\\out\\probe_inside.txt"
                                     : L"C:\\FACTOR\\probe\\out\\probe_outside.txt";
    wchar_t cmd[1024];
    _snwprintf_s(cmd, _TRUNCATE,
        L"\"C:\\FACTOR\\probe\\bin\\probe.exe\" --tag %s --secure-pipe %s --default-pipe %s --loopback-port %d",
        tag, PIPE_SECURE, PIPE_DEFAULT, loopPort);

    wprintf(L"CreateProcess attributes: EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT; "
            L"STARTF_USESTDHANDLES; %s\n",
            inside ? L"PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES{AppContainerSid=<pkg>,Capabilities=NULL,CapabilityCount=0} + "
                     L"PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY=PROCESS_CREATION_CHILD_PROCESS_RESTRICTED + PROC_THREAD_ATTRIBUTE_HANDLE_LIST"
                   : L"no security-capabilities attribute (control) + PROC_THREAD_ATTRIBUTE_HANDLE_LIST");

    int rc = launchChild(L"C:\\FACTOR\\probe\\bin\\probe.exe", cmd, PATH_BIN, outFile, inside, 60000);

    SetEvent(g_hStop);
    if (tSec) { WaitForSingleObject(tSec, 3000); CloseHandle(tSec); }
    if (tDef) { WaitForSingleObject(tDef, 3000); CloseHandle(tDef); }
    if (hSec != INVALID_HANDLE_VALUE) CloseHandle(hSec);
    if (hDef != INVALID_HANDLE_VALUE) CloseHandle(hDef);
    CloseHandle(sSec.hEvent); CloseHandle(sDef.hEvent); CloseHandle(g_hStop);
    if (g_listen != INVALID_SOCKET) { closesocket(g_listen); g_listen = INVALID_SOCKET; }
    return rc;
}

static int runLlama(bool inside, const wchar_t* model, const wchar_t* exe) {
    if (!ensureProfile(true)) return 2;
    const wchar_t* llamaDir = L"C:\\llama.cpp";
    if (inside) {
        wprintf(L"ACL grants for llama-inside:\n");
        grantSid(llamaDir, GENERIC_READ | GENERIC_EXECUTE, true);
        grantSid(model, GENERIC_READ, false);
        grantSid(PATH_OUT, GENERIC_READ | GENERIC_WRITE | GENERIC_EXECUTE, true);
    }
    const wchar_t* outFile = inside ? L"C:\\FACTOR\\probe\\out\\llama_inside.txt"
                                    : L"C:\\FACTOR\\probe\\out\\llama_outside.txt";
    wchar_t cmd[1400];
    _snwprintf_s(cmd, _TRUNCATE,
        L"\"%s\" -m \"%s\" -ngl 99 -p 128 -n 32 -r 2", exe, model);
    wprintf(L"llama cmd: %s\n", cmd);
    int rc = launchChild(exe, cmd, llamaDir, outFile, inside, 240000);
    return rc;
}

static int cleanup() {
    ensureProfile(false);
    wprintf(L"Cleanup: revoking package-SID ACEs\n");
    revokeSid(PATH_BIN);
    revokeSid(PATH_OUT);
    revokeSid(L"C:\\llama.cpp");
    revokeSid(L"C:\\models\\q3-17b-emit-G2-Q4_K_M.gguf");
    revokeSid(L"C:\\models\\all-MiniLM-L6-v2-ggml-model-f16.gguf");
    HRESULT hr = DeleteAppContainerProfile(AC_NAME);
    wprintf(L"DeleteAppContainerProfile(FACTOR-probe) hr=0x%08lX\n", (unsigned long)hr);
    return SUCCEEDED(hr) ? 0 : 1;
}

// ----------------------------------------------------------------------------
int wmain(int argc, wchar_t** argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (argc < 2) { wprintf(L"usage: launcher <ensure|probe-outside|probe-inside|llama-outside|llama-inside|cleanup> ...\n"); return 1; }
    const wchar_t* mode = argv[1];
    if (!wcscmp(mode, L"ensure"))        return ensureProfile(true) ? 0 : 2;
    if (!wcscmp(mode, L"probe-outside")) return runProbe(false);
    if (!wcscmp(mode, L"probe-inside"))  return runProbe(true);
    if (!wcscmp(mode, L"llama-outside")) { if (argc < 4) { wprintf(L"need <model> <exe>\n"); return 1; } return runLlama(false, argv[2], argv[3]); }
    if (!wcscmp(mode, L"llama-inside"))  { if (argc < 4) { wprintf(L"need <model> <exe>\n"); return 1; } return runLlama(true, argv[2], argv[3]); }
    if (!wcscmp(mode, L"cleanup"))       return cleanup();
    wprintf(L"unknown mode\n");
    return 1;
}
