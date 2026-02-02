"use client";

import React, { useState, useRef } from "react";
import {
  Upload,
  Video,
  Settings,
  Play,
  Download,
  ChevronRight,
  FileText,
  User,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  Layers,
  Palette,
  Brain,
  Clock,
  Cloud,
  Zap
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

// --- Types ---
type GenerationStep = {
  id: number;
  label: string;
  description: string;
};

const STEPS: GenerationStep[] = [
  { id: 1, label: "Ingestion", description: "Parsing your document and extracting text..." },
  { id: 2, label: "Analysis", description: "Claude 3.5 / Llama analyzing concepts..." },
  { id: 3, label: "Slides", description: "Designing premium educational slides with diagrams..." },
  { id: 4, label: "Scripts", description: "Writing conversational teaching scripts..." },
  { id: 5, label: "Voice", description: "Generating AI voiceover narration..." },
  { id: 6, label: "Avatar", description: "Syncing lip movements (if enabled)..." },
  { id: 7, label: "Composition", description: "Assembling final video layers..." },
];

const PROVIDERS = [
  { id: "groq", name: "Groq (Fast & Free)", icon: Zap, desc: "Llama 3.3 / DeepSeek" },
  { id: "amazon_bedrock", name: "AWS Bedrock (Production)", icon: Cloud, desc: "Claude 3.5 Sonnet" },
];

const MODELS = [
  { id: "llama-3.3-70b-versatile", name: "Llama 3.3 (Fast)", icon: Sparkles },
  { id: "deepseek-r1-distill-llama-70b", name: "DeepSeek R1 (Deep Reasoning)", icon: Settings },
  { id: "llama-3.2-90b-vision-preview", name: "Llama 3.2 Vision (Charts & PDF Visuals)", icon: Video },
];

const THEMES = [
  { id: "modern_dark", name: "Modern Dark", color: "#6366f1", desc: "Professional slate & indigo" },
  { id: "cyber_neon", name: "Cyber Neon", color: "#00ffff", desc: "High-tech black & cyan" },
  { id: "elegant_light", name: "Elegant Light", color: "#1e293b", desc: "Clean white & navy" },
  { id: "corporate_pro", name: "Corporate Pro", color: "#1a365d", desc: "Formal blue & grey" },
];

const API_BASE_URL = "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [avatar, setAvatar] = useState<File | null>(null);
  const [useAvatar, setUseAvatar] = useState(true);
  const [isIntelligent, setIsIntelligent] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(PROVIDERS[0].id);
  const [selectedModel, setSelectedModel] = useState(MODELS[0].id);
  const [selectedTheme, setSelectedTheme] = useState(THEMES[0].id);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [resultVideo, setResultVideo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const avatarInputRef = useRef<HTMLInputElement>(null);

  const handleGenerate = async () => {
    if (!file) return;

    setIsGenerating(true);
    setResultVideo(null);
    setError(null);
    setCurrentStep(1);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", selectedModel);
    formData.append("theme", selectedTheme);
    formData.append("intelligence", isIntelligent ? "intelligent" : "standard");
    formData.append("provider", selectedProvider);

    if (useAvatar && avatar) {
      formData.append("avatar_image", avatar);
    }

    const delay = isIntelligent ? 30000 : 15000;
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < 7) return prev + 1;
        return prev;
      });
    }, delay);

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-video`, formData);

      if (response.data.status === "success") {
        setResultVideo(`${API_BASE_URL}${response.data.download_url}`);
        setCurrentStep(7);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate video. Please ensure the backend is running and AWS credentials are set if using Bedrock.");
    } finally {
      clearInterval(stepInterval);
      setIsGenerating(false);
    }
  };

  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      <header className="text-center mb-16 px-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6"
        >
          <Sparkles className="w-4 h-4" />
          <span>Next-Gen AI Video Educator</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent mb-6"
        >
          Documents to Lessons
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed"
        >
          Enterprise-ready video generation using Claude 3.5 on AWS Bedrock or fast Llama on Groq.
        </motion.p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card rounded-3xl p-8 space-y-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/20 text-primary">
              <Upload className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-semibold">Upload Content</h2>
          </div>

          <div
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer border-2 border-dashed rounded-2xl p-8 transition-all hover:border-primary/50 hover:bg-white/5 group ${file ? "border-primary bg-primary/5" : "border-slate-700"}`}
          >
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              accept=".pdf,.docx,.txt"
            />
            <div className="flex flex-col items-center text-center gap-3">
              <FileText className={`w-12 h-12 transition-colors ${file ? "text-primary" : "text-slate-500 group-hover:text-slate-400"}`} />
              <div>
                <p className="font-medium text-lg">{file ? file.name : "Select Document"}</p>
                <p className="text-slate-500 text-sm">PDF, DOCX, or TXT up to 20MB</p>
              </div>
            </div>
          </div>

          {/* Provider Selection */}
          <div className="space-y-4 pt-4 border-t border-slate-700/50">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
                <Cloud className="w-5 h-5" />
              </div>
              <h3 className="font-semibold">AI Provider</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {PROVIDERS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProvider(p.id)}
                  className={`flex flex-col gap-1 p-4 rounded-xl border transition-all text-left ${selectedProvider === p.id ? "border-blue-500 bg-blue-500/10 ring-1 ring-blue-500" : "border-slate-700 hover:border-slate-500 hover:bg-white/5"}`}
                >
                  <div className="flex items-center gap-2">
                    <p.icon className={`w-4 h-4 ${selectedProvider === p.id ? "text-blue-400" : "text-slate-500"}`} />
                    <span className={`text-sm font-bold ${selectedProvider === p.id ? "text-white" : "text-slate-400"}`}>{p.name}</span>
                  </div>
                  <p className="text-[10px] text-slate-500">{p.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {selectedProvider === "groq" && (
            <div className="space-y-4 pt-4 border-t border-slate-700/50">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-accent/20 text-accent">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="font-semibold">Groq Model</h3>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {MODELS.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => setSelectedModel(model.id)}
                    className={`flex items-center justify-between p-4 rounded-xl border transition-all text-left ${selectedModel === model.id ? "border-primary bg-primary/10 ring-1 ring-primary" : "border-slate-700 hover:border-slate-500 hover:bg-white/5"}`}
                  >
                    <div className="flex items-center gap-3">
                      <model.icon className={`w-5 h-5 ${selectedModel === model.id ? "text-primary" : "text-slate-500"}`} />
                      <span className={`text-sm font-medium ${selectedModel === model.id ? "text-white" : "text-slate-400"}`}>{model.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
                  <Brain className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-bold text-white">INTELLIGENT MODE</p>
                    <span className="px-1.5 py-0.5 rounded bg-indigo-500 text-[10px] font-black text-white">PRO</span>
                  </div>
                  <p className="text-xs text-slate-400">Deep scan PDF + Longer, detailed scripts</p>
                </div>
              </div>
              <button
                onClick={() => setIsIntelligent(!isIntelligent)}
                className={`w-14 h-7 rounded-full transition-all relative p-1 ${isIntelligent ? "bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]" : "bg-slate-700"}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform ${isIntelligent ? "translate-x-7" : "translate-x-0"}`} />
              </button>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-slate-700/50">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-secondary/20 text-secondary">
                <Palette className="w-5 h-5" />
              </div>
              <h3 className="font-semibold">Slide Theme</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {THEMES.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => setSelectedTheme(theme.id)}
                  className={`flex flex-col gap-2 p-4 rounded-xl border transition-all text-left ${selectedTheme === theme.id ? "border-primary bg-primary/10 ring-1 ring-primary" : "border-slate-700 hover:border-slate-500 hover:bg-white/5"}`}
                >
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: theme.color }} />
                    <span className={`text-sm font-medium ${selectedTheme === theme.id ? "text-white" : "text-slate-400"}`}>{theme.name}</span>
                  </div>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider">{theme.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-slate-700/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-secondary/20 text-secondary">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-medium">AI Presenter</p>
                  <p className="text-xs text-slate-500">Lip-synced talking avatar</p>
                </div>
              </div>
              <button
                onClick={() => setUseAvatar(!useAvatar)}
                className={`w-12 h-6 rounded-full transition-colors relative ${useAvatar ? "bg-primary" : "bg-slate-700"}`}
              >
                <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${useAvatar ? "translate-x-6" : ""}`} />
              </button>
            </div>
            <AnimatePresence>
              {useAvatar && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                  <div onClick={() => avatarInputRef.current?.click()} className={`cursor-pointer border rounded-xl p-4 transition-all hover:bg-white/5 flex items-center gap-4 ${avatar ? "border-primary bg-primary/5" : "border-slate-700"}`}>
                    <input type="file" ref={avatarInputRef} className="hidden" onChange={(e) => setAvatar(e.target.files?.[0] || null)} accept="image/*" />
                    {avatar ? <img src={URL.createObjectURL(avatar)} className="w-12 h-12 rounded-lg object-cover" /> : <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center"><Upload className="w-5 h-5 text-slate-500" /></div>}
                    <div>
                      <p className="text-sm font-medium">{avatar ? avatar.name : "Upload Face Photo"}</p>
                      <p className="text-xs text-slate-500">JPG or PNG</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            onClick={handleGenerate}
            disabled={!file || isGenerating || (useAvatar && !avatar)}
            className="w-full bg-gradient-to-r from-primary to-secondary text-white py-4 rounded-2xl font-semibold text-lg hover:shadow-lg hover:shadow-primary/20 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isGenerating ? <><Loader2 className="w-6 h-6 animate-spin" /> Generating...</> : <><Play className="w-6 h-6 fill-current" /> Generate Lessons</>}
          </button>

          {error && <div className="p-4 rounded-xl bg-accent/10 border border-accent/20 text-accent flex items-center gap-3"><AlertCircle className="w-5 h-5 flex-shrink-0" /><p className="text-sm">{error}</p></div>}
        </motion.div>

        <div className="space-y-8">
          <AnimatePresence mode="wait">
            {isGenerating ? (
              <motion.div key="progress" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 1.05 }} className="glass-card rounded-3xl p-8 transition-all">
                <h3 className="text-xl font-semibold mb-8 flex items-center gap-3"><div className="w-2 h-2 rounded-full bg-primary animate-pulse" /> Processing Pipeline</h3>
                <div className="space-y-6">
                  {STEPS.map((step) => {
                    const isActive = currentStep === step.id;
                    const isCompleted = currentStep > step.id;
                    return (
                      <div key={step.id} className="flex gap-4 group">
                        <div className="flex flex-col items-center">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${isCompleted ? "bg-green-500/20 text-green-500" : isActive ? "bg-primary text-white shadow-lg shadow-primary/30" : "bg-slate-800 text-slate-500"}`}>
                            {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : step.id}
                          </div>
                          {step.id < 7 && <div className={`w-0.5 h-full my-1 transition-colors ${isCompleted ? "bg-green-500/20" : "bg-slate-800"}`} />}
                        </div>
                        <div className="pb-4">
                          <p className={`font-semibold ${isActive ? "text-white" : "text-slate-400 group-hover:text-slate-300"}`}>{step.label}</p>
                          <p className="text-xs text-slate-500 mt-1 max-w-[250px]">{step.description}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            ) : resultVideo ? (
              <motion.div key="result" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card rounded-3xl p-8 overflow-hidden">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold">Ready to Watch</h3>
                  <a href={resultVideo} download className="p-2 rounded-lg bg-green-500/20 text-green-500 hover:bg-green-500/30 transition-colors"><Download className="w-5 h-5" /></a>
                </div>
                <video src={resultVideo} controls className="w-full aspect-video rounded-2xl bg-black shadow-xl" autoPlay />
                <div className="mt-8 grid grid-cols-2 gap-4">
                  <button onClick={() => { setResultVideo(null); setFile(null); setAvatar(null); }} className="p-4 rounded-xl border border-slate-700 text-slate-400 hover:bg-white/5 transition-colors font-medium">Start New</button>
                  <a href={resultVideo} target="_blank" className="p-4 rounded-xl bg-primary text-white text-center font-medium hover:bg-primary/90 transition-colors">Open Full</a>
                </div>
              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-slate-800 rounded-3xl text-slate-600">
                <div className="p-6 rounded-full bg-slate-900 mb-6"><Video className="w-16 h-16 opacity-20" /></div>
                <p className="text-lg font-medium opacity-50">Nothing here yet</p>
                <p className="max-w-[200px] text-sm mt-2 opacity-30">Upload a document on the left to start generating your AI lesson.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <footer className="mt-20 pt-10 border-t border-slate-700/50 flex flex-col md:flex-row justify-between items-center gap-6 text-slate-500 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span>Backend Connected: Localhost:8000</span>
        </div>
        <p>© 2026 AI Video Generator. Built with AWS Bedrock & Groq.</p>
      </footer>
    </main>
  );
}
