import React, { useEffect, useRef, useState } from 'react'
import * as Tone from 'tone'
import { useDawStore } from '../state/dawStore'

export const Timeline: React.FC<{ totalSec:number; onScrub:(sec:number)=>void }>=({ totalSec, onScrub })=>{
  const { pxPerSecond, setZoom, cursorSec, setCursor, snap, bpm, timeSig } = useDawStore()
  const ref = useRef<HTMLDivElement>(null)
  const [scrollLeft, setScrollLeft] = useState(0)

  // Mouse wheel zoom + scroll
  useEffect(()=>{
    const el = ref.current; if(!el) return
    const onWheel = (e:WheelEvent)=>{
      if (e.ctrlKey || e.metaKey) { // zoom
        e.preventDefault()
        const z = pxPerSecond * (e.deltaY < 0 ? 1.1 : 0.9)
        setZoom(z)
      }
    }
    el.addEventListener('wheel', onWheel, { passive: false })
    return ()=> el.removeEventListener('wheel', onWheel as any)
  }, [pxPerSecond, setZoom])

  // Scrub & snap
  const onDown:React.MouseEventHandler<HTMLDivElement> = (e)=>{
    const bounds = (e.currentTarget as HTMLDivElement).getBoundingClientRect()
    const x = e.clientX - bounds.left + e.currentTarget.scrollLeft
    let sec = x / pxPerSecond
    if (snap){
      const spb = 60 / bpm
      const q = spb/2 // 8th-note grid
      sec = Math.round(sec / q) * q
    }
    setCursor(sec)
    onScrub(sec)
  }

  // Auto-scroll when playing
  useEffect(()=>{
    let r = 0
    const loop = ()=>{
      const sec = Tone.Transport.seconds
      useDawStore.setState({ cursorSec: sec })
      if (ref.current){
        const x = sec * pxPerSecond
        const viewL = ref.current.scrollLeft
        const viewR = viewL + ref.current.clientWidth
        if (x > viewR - 80) ref.current.scrollLeft = x - ref.current.clientWidth/2
      }
      r = requestAnimationFrame(loop)
    }
    r = requestAnimationFrame(loop)
    return ()=> cancelAnimationFrame(r)
  }, [pxPerSecond])

  return (
    <div ref={ref} className="relative h-20 overflow-x-auto bg-neutral-900" onMouseDown={onDown}
         onScroll={(e)=> setScrollLeft((e.target as HTMLDivElement).scrollLeft)}>
      <div style={{ width: totalSec*pxPerSecond }} className="h-full relative">
        {/* Cursor */}
        <div className="absolute top-0 bottom-0 w-px bg-emerald-400" style={{ left: cursorSec*pxPerSecond }}/>
      </div>
    </div>
  )
}
