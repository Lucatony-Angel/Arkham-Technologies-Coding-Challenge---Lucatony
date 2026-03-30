import { useEffect, useState } from "react";
import { fetchOutages, fetchAnalytics, triggerRefresh } from "./services/api";

const PAGE_SIZE = 100;
const COLUMNS = ["period", "capacity_mw", "outage_mw", "percent_outage"];

export default function App() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(null);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortCol, setSortCol] = useState("period");
  const [sortAsc, setSortAsc] = useState(false);
  const [refreshMsg, setRefreshMsg] = useState(null);
  const [analytics, setAnalytics] = useState([]);

  async function load(newOffset = 0) {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchOutages({
        limit: PAGE_SIZE,
        offset: newOffset,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      });
      setRows(result.data);
      setTotal(result.total);
      setOffset(newOffset);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadAnalytics() {
    try {
      const result = await fetchAnalytics();
      setAnalytics(result.data);
    } catch (e) {
      // analytics failure is non-critical, don't block the main view
    }
  }

  useEffect(() => { load(0); loadAnalytics(); }, [dateFrom, dateTo]);

  async function handleRefresh() {
    setLoading(true);
    setError(null);
    setRefreshMsg(null);
    try {
      const result = await triggerRefresh();
      setRefreshMsg(`Refreshed — ${result.row_count} rows ingested.`);
      await load(0);
      await loadAnalytics();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSort(col) {
    if (sortCol === col) {
      setSortAsc((a) => !a);
    } else {
      setSortCol(col);
      setSortAsc(true);
    }
  }

  const sorted = [...rows].sort((a, b) => {
    const av = a[sortCol];
    const bv = b[sortCol];
    if (av < bv) return sortAsc ? -1 : 1;
    if (av > bv) return sortAsc ? 1 : -1;
    return 0;
  });

  return (
    <div className="container">
      <h1>US Nuclear Outages</h1>

      <div className="toolbar">
        <div className="filters">
          <label>
            From
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          </label>
          <label>
            To
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          </label>
        </div>
        <button onClick={handleRefresh} disabled={loading}>
          {loading ? "Loading…" : "Refresh Data"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {refreshMsg && <div className="success">{refreshMsg}</div>}

      {!loading && rows.length === 0 && !error && (
        <div className="empty">No outage data found. Try refreshing.</div>
      )}

      {sorted.length > 0 && (
        <>
          <table>
            <thead>
              <tr>
                {COLUMNS.map((col) => (
                  <th key={col} onClick={() => handleSort(col)} className="sortable">
                    {col} {sortCol === col ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.map((row) => (
                <tr key={row.period}>
                  <td>{row.period}</td>
                  <td>{row.capacity_mw.toLocaleString()}</td>
                  <td>{row.outage_mw.toLocaleString()}</td>
                  <td>{row.percent_outage.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <button onClick={() => load(offset - PAGE_SIZE)} disabled={offset === 0 || loading}>
              Previous
            </button>
            <span>Showing {offset + 1}–{offset + rows.length}</span>
            <button onClick={() => load(offset + PAGE_SIZE)} disabled={offset + rows.length >= total || loading}>
              Next
            </button>
          </div>
        </>
      )}

      {analytics.length > 0 && (
        <>
          <h2>Monthly Analytics</h2>
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Month</th>
                <th>Avg Outage %</th>
                <th>Avg Outage MW</th>
                <th>Avg Capacity MW</th>
              </tr>
            </thead>
            <tbody>
              {analytics.map((row) => (
                <tr key={`${row.year}-${row.month}`}>
                  <td>{row.year}</td>
                  <td>{row.month}</td>
                  <td>{row.avg_outage_pct.toFixed(2)}%</td>
                  <td>{row.avg_outage_mw.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                  <td>{row.avg_capacity_mw.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
