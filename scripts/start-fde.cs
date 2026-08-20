using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;

// ============================================================
// FDE 学习中心 · 一键启动器（源码）
// 功能：自动检查环境/依赖 → 自动选择可用端口 → 启动 Docusaurus
//       开发服务器 → 等待编译完成 → 自动打开浏览器预览
// 重新编译：双击 scripts\rebuild-launcher.bat
// 编译命令：csc /target:exe /codepage:65001 /out:FDE一键启动.exe start-fde.cs
// ============================================================

namespace FdeLauncher
{
    internal static class Program
    {
        private const string SitePath = "/";
        // 兜底项目路径：exe 不在项目目录内时使用（便于从任意位置创建快捷方式）
        private const string FallbackProjectDir = @"f:\AICoding\fde-learning-master";

        private static string _projectDir = "";
        private static string _cmdPath = "";

        private static int Main(string[] args)
        {
            try { Console.OutputEncoding = Encoding.UTF8; } catch { }
            try { Console.Title = "FDE 学习中心 · 一键启动器"; } catch { }
            _cmdPath = Path.Combine(Environment.SystemDirectory, "cmd.exe");
            if (!File.Exists(_cmdPath)) _cmdPath = "cmd.exe";

            PrintBanner();

            // 1. 定位项目目录
            _projectDir = FindProjectDir(AppDomain.CurrentDomain.BaseDirectory);
            if (_projectDir == null && IsProjectDir(FallbackProjectDir)) _projectDir = FallbackProjectDir;
            if (_projectDir == null)
            {
                Fail("未找到项目目录。请把本程序放在项目根目录（包含 package.json 和 docusaurus.config.js 的目录）后重试。");
                return 1;
            }
            StepOk("定位项目目录", _projectDir);

            // 2. 检测服务器是否已在运行（支持重复双击）
            string existing = FindRunningSite();
            if (existing != null)
            {
                WriteColor("[提示] 检测到开发服务器已在运行：" + existing, ConsoleColor.Yellow);
                WriteColor("       已直接打开浏览器。如需重启服务器，请先关闭之前运行它的窗口。", ConsoleColor.Yellow);
                OpenBrowser(existing);
                return 0;
            }

            // 3. 检查 Node.js / npm
            string nodeVer;
            if (RunCapture(_cmdPath, "/c node --version", _projectDir, out nodeVer) != 0 || string.IsNullOrEmpty(nodeVer))
            {
                Fail("未检测到 Node.js。请先安装 Node.js 18 或更高版本：https://nodejs.org/");
                return 1;
            }
            string npmVer;
            if (RunCapture(_cmdPath, "/c npm --version", _projectDir, out npmVer) != 0 || string.IsNullOrEmpty(npmVer))
            {
                Fail("未检测到 npm。请重新完整安装 Node.js：https://nodejs.org/");
                return 1;
            }
            StepOk("检查 Node.js 环境", nodeVer + "  (npm " + npmVer + ")");

            // 4. 检查依赖，缺失则自动安装
            if (Directory.Exists(Path.Combine(_projectDir, "node_modules")))
            {
                StepOk("检查项目依赖", "已安装");
            }
            else
            {
                WriteColor("[步骤] 首次运行，正在安装依赖（约 2~5 分钟，请勿关闭窗口）……", ConsoleColor.Yellow);
                int installCode = RunWait(_cmdPath, "/c npm install");
                if (installCode != 0 || !Directory.Exists(Path.Combine(_projectDir, "node_modules")))
                {
                    Fail("依赖安装失败。请在项目目录手动执行 npm install 查看详细报错。");
                    return 1;
                }
                StepOk("安装项目依赖", "完成");
            }

            // 5. 选择端口（3000 被占用时自动顺延）
            int port;
            if (args.Length > 0 && IsPortNumber(args[0], out port))
            {
                if (!IsPortFree(port))
                {
                    Fail("指定的端口 " + port + " 已被占用。请先关闭占用该端口的程序，或换一个端口运行本程序。");
                    return 1;
                }
            }
            else
            {
                port = ChooseFreePort(3000);
            }
            string portNote = port == 3000 ? "" : "（3000 已被占用，自动改用）";
            StepOk("选择端口", port.ToString() + " " + portNote);

            // 6. 启动开发服务器（绑定 127.0.0.1，避免 IPv4/IPv6 解析歧义）
            Console.WriteLine();
            WriteColor("[步骤] 正在启动开发服务器（服务器日志将显示在下方）……", ConsoleColor.Cyan);
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = _cmdPath;
            psi.Arguments = "/c npm start -- --port " + port + " --host 127.0.0.1 --no-open";
            psi.WorkingDirectory = _projectDir;
            psi.UseShellExecute = false;
            psi.CreateNoWindow = false;
            Process server = Process.Start(psi);
            int serverPid = server.Id;
            AppDomain.CurrentDomain.ProcessExit += delegate { KillTree(serverPid); };

            // 7. 等待编译完成（首次约 1~2 分钟）
            string url = "http://127.0.0.1:" + port + SitePath;
            Console.Write("[等待] 服务器编译中");
            bool ready = WaitForReady(url, 300, server);
            Console.WriteLine();
            if (!ready)
            {
                KillTree(serverPid);
                Fail("服务器未能就绪。请查看上方日志排查（常见原因：Node 版本过低、依赖损坏，可删除 node_modules 后重试）。");
                return 1;
            }

            // 8. 编译完成，打开浏览器
            Console.WriteLine();
            WriteColor("==================================================", ConsoleColor.Green);
            WriteColor("  启动成功！浏览器即将自动打开：", ConsoleColor.White);
            WriteColor("  " + url, ConsoleColor.White);
            WriteColor("==================================================", ConsoleColor.Green);
            Console.WriteLine();
            Console.WriteLine("  使用提示：");
            Console.WriteLine("    - 修改 docs/ 目录下的 Markdown 并保存，浏览器会自动刷新");
            Console.WriteLine("    - 停止服务器：关闭本窗口，或在本窗口按 Ctrl+C");
            Console.WriteLine();
            OpenBrowser(url);

            server.WaitForExit();
            WriteColor("[提示] 开发服务器已退出。", ConsoleColor.Yellow);
            Pause();
            return 0;
        }

        // ---------- 就绪检测 ----------

        // 轮询首页，直到返回 200 且包含站点标识，且 JS 资源已可访问（编译完成）
        private static bool WaitForReady(string url, int timeoutSeconds, Process server)
        {
            DateTime start = DateTime.Now;
            DateTime deadline = start.AddSeconds(timeoutSeconds);
            bool hintShown = false;
            while (DateTime.Now < deadline)
            {
                if (server.HasExited) return false;
                Console.Write(".");
                int code;
                string html = HttpGet(url, 15000, true, out code);
                if (code == 200 && html.IndexOf("FDE", StringComparison.Ordinal) >= 0
                    && AssetsReady(url, html, deadline))
                {
                    return true;
                }
                if (!hintShown && (DateTime.Now - start).TotalSeconds > 60)
                {
                    Console.Write("（首次编译较慢，请耐心等待）");
                    hintShown = true;
                }
                Thread.Sleep(1500);
            }
            return false;
        }

        // 页面 HTML 里任一 JS 资源可正常返回，说明 webpack 编译已产出
        private static bool AssetsReady(string pageUrl, string html, DateTime deadline)
        {
            List<string> urls = new List<string>();
            try
            {
                Uri page = new Uri(pageUrl);
                foreach (Match m in Regex.Matches(html, "<script[^>]*\\ssrc=\"([^\"]+)\""))
                {
                    string src = m.Groups[1].Value;
                    if (string.IsNullOrEmpty(src)) continue;
                    if (src.StartsWith("http://", StringComparison.OrdinalIgnoreCase)) continue;
                    if (src.StartsWith("https://", StringComparison.OrdinalIgnoreCase)) continue;
                    try
                    {
                        Uri abs = src.StartsWith("/")
                            ? new Uri("http://127.0.0.1:" + page.Port + src)
                            : new Uri(page, src);
                        if (!urls.Contains(abs.ToString())) urls.Add(abs.ToString());
                    }
                    catch { }
                }
            }
            catch { }
            if (urls.Count == 0) return true;
            foreach (string u in urls)
            {
                if (DateTime.Now >= deadline) return false;
                int code;
                HttpGet(u, 30000, false, out code);
                if (code == 200) return true;
            }
            return false;
        }

        // 检测本机常见端口上是否已有本站在运行
        private static string FindRunningSite()
        {
            int[] ports = new int[] { 3000, 3001, 3002, 3003 };
            string[] hosts = new string[] { "127.0.0.1", "localhost", "[::1]" };
            foreach (int p in ports)
            {
                foreach (string h in hosts)
                {
                    string url = "http://" + h + ":" + p + SitePath;
                    int code;
                    string html = HttpGet(url, 2500, true, out code);
                    if (code == 200 && html.IndexOf("FDE", StringComparison.Ordinal) >= 0) return url;
                }
            }
            return null;
        }

        // ---------- HTTP ----------

        private static string HttpGet(string url, int timeoutMs, bool readBody, out int code)
        {
            code = 0;
            HttpWebResponse resp = null;
            try
            {
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
                req.Method = "GET";
                req.Timeout = timeoutMs;
                req.ReadWriteTimeout = timeoutMs;
                req.Accept = "text/html,application/xhtml+xml,*/*";
                req.UserAgent = "Mozilla/5.0 (FDE-Launcher)";
                req.Proxy = null;
                resp = (HttpWebResponse)req.GetResponse();
                code = (int)resp.StatusCode;
                if (!readBody || code != 200) return "";
                using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                {
                    char[] buf = new char[65536];
                    int n = sr.Read(buf, 0, buf.Length);
                    return n > 0 ? new string(buf, 0, n) : "";
                }
            }
            catch (WebException ex)
            {
                if (ex.Response != null)
                {
                    try { code = (int)((HttpWebResponse)ex.Response).StatusCode; } catch { }
                }
                return "";
            }
            catch { return ""; }
            finally
            {
                if (resp != null) { try { resp.Close(); } catch { } }
            }
        }

        // ---------- 进程与端口 ----------

        private static bool IsPortNumber(string s, out int port)
        {
            port = 0;
            if (string.IsNullOrEmpty(s)) return false;
            if (!int.TryParse(s, out port)) return false;
            return port > 0 && port < 65536;
        }

        private static int ChooseFreePort(int start)
        {
            for (int p = start; p < start + 50; p++)
            {
                if (IsPortFree(p)) return p;
            }
            return start + 100;
        }

        private static bool IsPortFree(int port)
        {
            TcpListener l = null;
            try
            {
                l = new TcpListener(IPAddress.Loopback, port);
                l.Start();
                return true;
            }
            catch { return false; }
            finally
            {
                if (l != null) { try { l.Stop(); } catch { } }
            }
        }

        private static void KillTree(int pid)
        {
            try
            {
                string taskkill = Path.Combine(Environment.SystemDirectory, "taskkill.exe");
                if (!File.Exists(taskkill)) taskkill = "taskkill.exe";
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = taskkill;
                psi.Arguments = "/PID " + pid + " /T /F";
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                Process.Start(psi);
            }
            catch { }
        }

        private static void OpenBrowser(string url)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo(url);
                psi.UseShellExecute = true;
                Process.Start(psi);
            }
            catch (Exception ex)
            {
                WriteColor("[提示] 无法自动打开浏览器（" + ex.Message + "），请手动访问：" + url, ConsoleColor.Yellow);
            }
        }

        // ---------- 进程执行 ----------

        private static int RunCapture(string file, string args, string workDir, out string stdout)
        {
            stdout = "";
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = file;
                psi.Arguments = args;
                psi.WorkingDirectory = workDir;
                psi.UseShellExecute = false;
                psi.RedirectStandardOutput = true;
                psi.CreateNoWindow = true;
                using (Process p = Process.Start(psi))
                {
                    stdout = (p.StandardOutput.ReadToEnd() ?? "").Trim();
                    p.WaitForExit();
                    return p.ExitCode;
                }
            }
            catch { return -1; }
        }

        private static int RunWait(string file, string args)
        {
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = file;
            psi.Arguments = args;
            psi.WorkingDirectory = _projectDir;
            psi.UseShellExecute = false;
            using (Process p = Process.Start(psi))
            {
                p.WaitForExit();
                return p.ExitCode;
            }
        }

        // ---------- 目录定位 ----------

        private static string FindProjectDir(string startDir)
        {
            string dir = startDir;
            for (int i = 0; i < 6 && !string.IsNullOrEmpty(dir); i++)
            {
                if (IsProjectDir(dir)) return dir;
                string parent = null;
                try { parent = Path.GetDirectoryName(dir); } catch { }
                if (parent == null || parent == dir) break;
                dir = parent;
            }
            return null;
        }

        private static bool IsProjectDir(string dir)
        {
            if (string.IsNullOrEmpty(dir)) return false;
            try
            {
                return File.Exists(Path.Combine(dir, "package.json"))
                    && File.Exists(Path.Combine(dir, "docusaurus.config.js"));
            }
            catch { return false; }
        }

        // ---------- 界面 ----------

        private static void PrintBanner()
        {
            Console.WriteLine();
            WriteColor("==================================================", ConsoleColor.Cyan);
            WriteColor("        FDE 学习中心 · 一键启动器", ConsoleColor.White);
            WriteColor("  本地调试 · 自动装依赖 · 自动选端口 · 自动开浏览器", ConsoleColor.DarkGray);
            WriteColor("==================================================", ConsoleColor.Cyan);
            Console.WriteLine();
        }

        private static void StepOk(string name, string detail)
        {
            Console.Write("  [");
            Console.Write(name);
            Console.Write("] ");
            ConsoleColor old = Console.ForegroundColor;
            try { Console.ForegroundColor = ConsoleColor.Green; Console.Write("OK"); }
            finally { Console.ForegroundColor = old; }
            if (!string.IsNullOrEmpty(detail)) Console.WriteLine("  " + detail);
            else Console.WriteLine();
        }

        private static void Fail(string msg)
        {
            Console.WriteLine();
            WriteColor("[错误] " + msg, ConsoleColor.Red);
            Console.WriteLine();
            Pause();
        }

        private static void Pause()
        {
            Console.Write("按任意键关闭……");
            try { Console.ReadKey(true); } catch { }
        }

        private static void WriteColor(string text, ConsoleColor color)
        {
            ConsoleColor old = Console.ForegroundColor;
            try { Console.ForegroundColor = color; Console.WriteLine(text); }
            finally { Console.ForegroundColor = old; }
        }
    }
}
