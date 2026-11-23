import React, {useState} from 'react';
import { createRoot } from 'react-dom/client';
import Dashboard from './pages/Dashboard.jsx';
import DigitalTwin from './pages/DigitalTwin.jsx';
import EvidenceMonitor from './pages/EvidenceMonitor.jsx';
import AttackSimulator from './pages/AttackSimulator.jsx';
import BlockchainExplorer from './pages/BlockchainExplorer.jsx';
import ChainOfCustody from './pages/ChainOfCustody.jsx';
import ResultGenerator from './pages/ResultGenerator.jsx';
import './style.css';
const pages = {Dashboard, DigitalTwin, EvidenceMonitor, AttackSimulator, BlockchainExplorer, ChainOfCustody, ResultGenerator};
function App(){ const [page,setPage]=useState('Dashboard'); const Page=pages[page]; return <div><aside><h1>AquaForenChain</h1>{Object.keys(pages).map(p=><button key={p} onClick={()=>setPage(p)}>{p}</button>)}</aside><main><Page/></main></div> }
createRoot(document.getElementById('root')).render(<App/>);
