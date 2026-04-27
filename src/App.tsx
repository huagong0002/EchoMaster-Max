import { useState, useRef, useEffect, useMemo } from 'react';
import { 
  Play, Pause, RotateCcw, Settings2, BookOpen, Clock, Plus, Trash2, 
  Download, Upload, FastForward, Rewind, CheckCircle2, ListMusic, 
  ArrowRight, Save, Library, Folder, FileAudio, Calendar, ChevronRight, User as UserIcon, LogOut
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion'; // 确保包名正确
import Markdown from 'react-markdown';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- 基础配置 ---
const API_BASE = "https://www.sd-education.online"; // 强制指向后端主域名

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function App() {
  // 1. 用户与权限状态
  const [user, setUser] = useState<{ username: string; role: string; displayName: string } | null>(null);
  const [showAuthOverlay, setShowAuthOverlay] = useState(false);
  const [authData, setAuthData] = useState({ username: '', password: '' });
  const [authError, setAuthError] = useState<string | null>(null);

  // 2. 材料与列表状态
  const [materialList, setMaterialList] = useState<any[]>([]);
  const [material, setMaterial] = useState<any>({
    title: "未命名材料",
    audioUrl: "",
    segments: []
  });
  
  const [mode, setMode] = useState<'library' | 'setup' | 'edit'>('library');
  const [currentTime, setCurrentTime] = useState(0);
  const [activeSegmentIndex, setActiveSegmentIndex] = useState<number | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const lastUpdateRef = useRef(0);

  // --- 核心逻辑：获取数据 ---
  const fetchMaterials = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/materials`);
      if (res.ok) {
        const data = await res.json();
        setMaterialList(data);
        // 如果当前没有选中的材料，且库里有东西，默认显示第一个
        if (data.length > 0 && !material.audioUrl) {
          setMaterial(data[0]);
        }
      }
    } catch (err) {
      console.error("加载材料库失败", err);
    }
  };

  // 初始化检查登录状态
  useEffect(() => {
    const savedUser = localStorage.getItem('echomaster_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    fetchMaterials();
  }, []);

  // --- 登录逻辑修正 ---
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(authData)
      });
      const data = await res.json();
      if (res.ok) {
        setUser(data.user);
        localStorage.setItem('echomaster_user', JSON.stringify(data.user));
        setShowAuthOverlay(false);
        fetchMaterials(); // 登录成功立即刷新数据
      } else {
        setAuthError(data.message || "登录失败");
      }
    } catch (err) {
      setAuthError("网络连接失败，请检查主域名服务");
    }
  };

  // --- 保存并同步逻辑 ---
  const handleSaveToCloud = async () => {
    if (!user) return setShowAuthOverlay(true);
    setIsSyncing(true);
    try {
      const payload = {
        ...material,
        id: material.id || Math.random().toString(36).substr(2, 9),
        updatedBy: user.displayName,
        updatedAt: new Date().toISOString()
      };
      const res = await fetch(`${API_BASE}/api/materials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert("设置已保存并同步给全校用户！");
        fetchMaterials();
      }
    } catch (err) {
      alert("保存失败，请检查网络");
    } finally {
      setIsSyncing(false);
    }
  };

  // --- 播放时间更新（防闪烁节流） ---
  const onTimeUpdate = (e: any) => {
    const time = e.target.currentTime;
    // 每 0.2 秒才更新一次状态，大幅降低渲染压力，消除闪烁
    if (Math.abs(time - lastUpdateRef.current) > 0.2) {
      setCurrentTime(time);
      lastUpdateRef.current = time;
      
      const idx = material.segments.findIndex((s: any) => time >= s.startTime && time <= s.endTime);
      if (idx !== activeSegmentIndex) setActiveSegmentIndex(idx);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F172A] text-slate-200 font-sans selection:bg-blue-500/30">
      {/* 顶部导航栏：显示用户信息 */}
      <nav className="border-b border-white/5 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Library size={18} className="text-white" />
            </div>
            <span className="font-black tracking-tighter text-xl text-white">ECHO<span className="text-blue-500">MASTER</span></span>
          </div>

          <div className="flex items-center gap-4">
            {user ? (
              <div className="flex items-center gap-3 bg-white/5 px-4 py-1.5 rounded-full border border-white/10">
                <div className="text-right">
                  <p className="text-[10px] text-blue-400 font-black uppercase leading-none mb-1">{user.role}</p>
                  <p className="text-xs font-bold text-white">{user.displayName}</p>
                </div>
                <button onClick={() => { setUser(null); localStorage.removeItem('echomaster_user'); }} className="text-slate-500 hover:text-red-400 transition-colors">
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <button onClick={() => setShowAuthOverlay(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition-all">
                登录同步
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {mode === 'library' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 材料列表展示 */}
            {materialList.map((item) => (
              <div key={item.id} onClick={() => { setMaterial(item); setMode('edit'); }} className="p-6 bg-slate-800/50 rounded-3xl border border-white/5 hover:border-blue-500/50 cursor-pointer transition-all group">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-blue-500/10 rounded-2xl text-blue-400 group-hover:scale-110 transition-transform">
                    <FileAudio size={24} />
                  </div>
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{item.updatedBy || '系统'}</span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <div className="flex items-center gap-4 text-slate-400 text-xs">
                  <div className="flex items-center gap-1"><Clock size={12}/> {item.segments?.length || 0} 分段</div>
                </div>
              </div>
            ))}
            <div onClick={() => setMode('setup')} className="p-6 border-2 border-dashed border-white/5 rounded-3xl flex flex-col items-center justify-center text-slate-500 hover:border-blue-500/50 hover:text-blue-400 cursor-pointer transition-all">
              <Plus size={32} className="mb-2" />
              <span className="font-bold">新增材料</span>
            </div>
          </div>
        ) : (
          <div className="bg-slate-900 rounded-3xl p-8 border border-white/10 relative">
             <button onClick={() => setMode('library')} className="absolute top-8 left-8 text-slate-500 hover:text-white flex items-center gap-2 text-xs font-bold">
               <RotateCcw size={14} /> 返回库
             </button>
             
             <div className="max-w-2xl mx-auto text-center mt-8">
                <h2 className="text-3xl font-black text-white mb-4">{material.title}</h2>
                <audio 
                  ref={audioRef} 
                  src={material.audioUrl} 
                  onTimeUpdate={onTimeUpdate} 
                  controls 
                  className="w-full mt-6"
                />
                <button 
                  onClick={handleSaveToCloud} 
                  disabled={isSyncing}
                  className="mt-8 px-8 py-3 bg-green-600 hover:bg-green-500 text-white rounded-2xl font-bold flex items-center gap-2 mx-auto transition-all"
                >
                  <Save size={18} /> {isSyncing ? "同步中..." : "保存设置并共享"}
                </button>
             </div>
          </div>
        )}
      </main>

      {/* 登录弹窗 */}
      <AnimatePresence>
        {showAuthOverlay && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-md">
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900 border border-white/10 p-8 rounded-[40px] w-full max-w-md shadow-2xl">
              <h2 className="text-2xl font-black text-white mb-2">欢迎回来</h2>
              <p className="text-slate-400 text-sm mb-8">请登录以同步您的教学材料库</p>
              <form onSubmit={handleLogin} className="space-y-4">
                <input 
                  type="text" placeholder="账号" 
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 focus:border-blue-500 outline-none transition-all"
                  onChange={e => setAuthData({...authData, username: e.target.value})}
                />
                <input 
                  type="password" placeholder="密码" 
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 focus:border-blue-500 outline-none transition-all"
                  onChange={e => setAuthData({...authData, password: e.target.value})}
                />
                {authError && <p className="text-red-400 text-xs font-bold">{authError}</p>}
                <button type="submit" className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-black rounded-2xl transition-all flex items-center justify-center gap-2">
                  进入系统 <ArrowRight size={18} />
                </button>
                <button type="button" onClick={() => setShowAuthOverlay(false)} className="w-full text-slate-500 text-xs font-bold pt-2">取消</button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}