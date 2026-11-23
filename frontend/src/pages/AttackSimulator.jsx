import { useEffect, useState } from 'react';
import { getJSON } from '../services/api.js';
export default function AttackSimulator(){ const [rows,setRows]=useState([]); useEffect(()=>{getJSON('/incidents/scenarios').then(setRows).catch(()=>setRows([]));},[]); return <><h2>Attack & Incident Simulator</h2><ul>{rows.map((r,i)=><li key={i}>{r.scenario || r.expected}</li>)}</ul></>; }
