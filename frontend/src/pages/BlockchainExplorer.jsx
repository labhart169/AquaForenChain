import { useEffect, useState } from 'react';
import { getJSON } from '../services/api.js';
export default function BlockchainExplorer(){ const [s,setS]=useState(null); useEffect(()=>{getJSON('/blockchain/status').then(setS).catch(()=>setS({connected:false,message:'API unavailable'}));},[]); return <><h2>Blockchain Explorer</h2><pre>{JSON.stringify(s,null,2)}</pre></>; }
