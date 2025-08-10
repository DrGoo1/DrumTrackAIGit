import React, { useMemo } from 'react'
import { useDawStore } from '../state/dawStore'

export const BarsBeatsRuler: React.FC<{ seconds:number }>=({seconds})=>{
  const { bpm, timeSig, pxPerSecond } = useDawStore()
  const spb = 60 / bpm
  const barDur = spb * timeSig[0]
  const width = seconds * pxPerSecond
  const ticks = useMemo(()=>{
    const arr: {x:number,label:string,major:boolean}[]=[]
    for (let t=0, bar=1; t<=seconds+0.01; t+=spb/2){
      const isBar = Math.abs((t/barDur) - Math.round(t/barDur)) < 1e-3
      arr.push({ x: t*pxPerSecond, label: isBar? `${bar++}`: '', major: isBar })
    }
    return arr
  }, [seconds,bpm,timeSig,pxPerSecond])
  return (
    <div className="relative h-8 bg-neutral-950 text-neutral-300 select-none">
      {ticks.map((tk,i)=> (
        <div key={i} className="absolute" style={{left: tk.x}}>
          <div className={`w-px ${tk.major?'h-8 bg-white':'h-4 bg-neutral-600'}`}/>
          {tk.major && <div className="text-xs -mt-6 ml-1">{tk.label}</div>}
        </div>
      ))}
      <div className="absolute right-2 top-1 text-xs opacity-60">Bars/Beats</div>
    </div>
  )
}
