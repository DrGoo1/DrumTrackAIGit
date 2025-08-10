import create from 'zustand'

export type MidiEvent = { time_sec: number; lane: string; velocity?: number }
export type LaneMap = Record<string, MidiEvent[]>

interface ZoomState { pxPerSecond: number; setZoom: (v:number)=>void }
interface TransportState { playing:boolean; cursorSec:number; setPlaying:(b:boolean)=>void; setCursor:(s:number)=>void }
interface GridState { bpm:number; timeSig:[number,number]; snap:boolean; setBpm:(n:number)=>void; setTimeSig:(n:[number,number])=>void; setSnap:(b:boolean)=>void }
interface KitState { kitMap: Record<string,string>; setKit:(m:Record<string,string>)=>void }
interface SessionState { jobId:string; setJobId:(s:string)=>void }
interface GrooveState { grooveMetrics: any | null; setGrooveMetrics:(g:any)=>void }
interface LoopsState { refLoops: any[]; setRefLoops:(a:any[])=>void }
interface ReviewState { comments: any[]; setComments:(a:any[])=>void }

export const useDawStore = create<ZoomState & TransportState & GridState & KitState & SessionState & GrooveState & LoopsState & ReviewState>((set)=>({
  pxPerSecond: 120,
  setZoom:(v)=>set({pxPerSecond: Math.max(20, Math.min(600, v))}),
  playing:false,
  cursorSec:0,
  setPlaying:(b)=>set({playing:b}),
  setCursor:(s)=>set({cursorSec:s}),
  bpm:120,
  timeSig:[4,4],
  snap:true,
  setBpm:(n)=>set({bpm:n}),
  setTimeSig:(n)=>set({timeSig:n}),
  setSnap:(b)=>set({snap:b}),
  kitMap:{},
  setKit:(m)=>set({kitMap:m}),
  jobId: Math.random().toString(36).slice(2),
  setJobId:(s)=>set({jobId:s}),
  grooveMetrics:null,
  setGrooveMetrics:(g)=>set({grooveMetrics:g}),
  refLoops:[],
  setRefLoops:(a)=>set({refLoops:a}),
  comments:[],
  setComments:(a)=>set({comments:a}),
}))
