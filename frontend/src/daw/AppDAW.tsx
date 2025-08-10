import React, { useEffect, useState } from 'react'
import * as Tone from 'tone'
import { useDawStore } from './state/dawStore'
import { DrumEngine } from './audio/engine'
import { TransportBar } from './ui/TransportBar'
import { BarsBeatsRuler } from './ui/BarsBeatsRuler'
import { Timeline } from './ui/Timeline'
import { Mixer } from './ui/Mixer'
import { KitBuilderModal } from './ui/KitBuilderModal'
import { ExportDialog } from './ui/ExportDialog'
import { ImpactDrumsPanel } from './ui/ImpactDrumsPanel'
import { GrooveCoachPanel } from './ui/GrooveCoachPanel'
import { PocketTransferModal } from './ui/PocketTransferModal'
import { ReviewPanel } from './ui/ReviewPanel'

export const AppDAW: React.FC = () => {
  const { kitMap, setCursor } = useDawStore()
  const [engine, setEngine] = useState<DrumEngine|null>(null)
  const [kitOpen, setKitOpen] = useState(false)
  const [expOpen, setExpOpen] = useState(false)
  const [pocketOpen, setPocketOpen] = useState(false)
  const [impact, setImpact] = useState({
    low:{drive_type:'analog',drive_amount:0.2,snap:0.15,blend:0.5},
    high:{drive_type:'tape',drive_amount:0.12,snap:0.1,blend:0.35},
    space:{on:false,type:'algo',predelay_ms:15,duck:0.25}
  })

  useEffect(()=>{ setEngine(new DrumEngine(kitMap)) }, [kitMap])
  useEffect(()=>{ Tone.Transport.scheduleRepeat(()=>{}, '8n') }, [])
  const totalSec = 60 * 3

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <TransportBar />
      <div className="flex items-center gap-2 p-2 border-b border-neutral-800">
        <button className="px-3 py-1 bg-neutral-800 rounded" onClick={()=> setKitOpen(true)}>Kit Builder</button>
        <button className="px-3 py-1 bg-neutral-800 rounded" onClick={()=> setExpOpen(true)}>Export</button>
        <button className="px-3 py-1 bg-neutral-800 rounded" onClick={()=> setPocketOpen(true)}>Pocket Transfer</button>
        <div className="ml-auto text-xs opacity-70">Mousewheel + Ctrl/⌘ to Zoom</div>
      </div>

      <div className="grid grid-cols-12 gap-3 p-3">
        <div className="col-span-12">
          <BarsBeatsRuler seconds={totalSec} />
          <Timeline totalSec={totalSec} onScrub={(sec)=> setCursor(sec)} />
        </div>
        <div className="col-span-8 space-y-3">
          <Mixer engine={engine} />
          <ImpactDrumsPanel value={impact as any} onChange={setImpact as any} />
        </div>
        <div className="col-span-4 space-y-3">
          <GrooveCoachPanel />
          <ReviewPanel />
        </div>
      </div>

      <KitBuilderModal open={kitOpen} onClose={()=> setKitOpen(false)} />
      <ExportDialog open={expOpen} onClose={()=> setExpOpen(false)} />
      <PocketTransferModal open={pocketOpen} onClose={()=> setPocketOpen(false)} />
    </div>
  )
}
