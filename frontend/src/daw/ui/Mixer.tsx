import React, { useEffect, useRef } from 'react'
import { useDawStore } from '../state/dawStore'
import { DrumEngine } from '../audio/engine'

const LANES = ['kick','snare','hihat','tom','ride','crash']

export const Mixer: React.FC<{ engine: DrumEngine | null }>=({ engine })=>{
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(()=>{
    let raf = 0
    const draw = ()=>{
      const c = canvasRef.current; if(!c || !engine) { raf=requestAnimationFrame(draw); return }
      const g = c.getContext('2d')!
      const wf = engine.getWaveform()
      g.clearRect(0,0,c.width,c.height)
      g.strokeStyle = '#22c55e'; g.beginPath()
      for (let i=0;i<wf.length;i++){
        const x = (i / wf.length)*c.width
        const y = (1 - (wf[i]*0.5+0.5))*c.height
        if (i===0) g.moveTo(x,y); else g.lineTo(x,y)
      }
      g.stroke()
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return ()=> cancelAnimationFrame(raf)
  }, [engine])

  return (
    <div className="p-2 bg-neutral-950 text-white border-t border-neutral-800">
      <div className="text-sm mb-2 opacity-80">Mixer (with live waveform meter)</div>
      <canvas ref={canvasRef} width={800} height={80} className="w-full h-20 bg-black/60 rounded" />
      <div className="grid grid-cols-6 gap-3 mt-3">
        {LANES.map(l=> (
          <div key={l} className="bg-neutral-900 rounded p-2">
            <div className="text-xs mb-2 opacity-80">{l}</div>
            <input type="range" min={-24} max={6} defaultValue={0} className="w-full" />
            <div className="text-[10px] mt-1 opacity-60">Vol (dB)</div>
            <input type="range" min={-50} max={50} defaultValue={0} className="w-full" />
            <div className="text-[10px] mt-1 opacity-60">Pan</div>
          </div>
        ))}
      </div>
    </div>
  )
}
