import { useEffect, useState } from 'react';
import MetricCard from '../components/MetricCard.jsx';
import { getJSON } from '../services/api.js';
export default function Dashboard(){ const [data,setData]=useState(null); useEffect(()=>{getJSON('/dashboard/summary').then(setData).catch(()=>setData({events:'run backend first',evidence:'-',batches:'-',custody:'-'}));},[]); return <><h2>Dashboard</h2><div className="grid"><MetricCard title="Events" value={data?.events ?? '...'} /><MetricCard title="Evidence" value={data?.evidence ?? '...'} /><MetricCard title="Batches" value={data?.batches ?? '...'} /><MetricCard title="Custody" value={data?.custody ?? '...'} /></div></>; }
