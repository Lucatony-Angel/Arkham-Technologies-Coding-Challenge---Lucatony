export async function fetchOutages({ limit = 100, offset = 0, date_from, date_to } = {}) {
  const params = new URLSearchParams({ limit, offset });
  if (date_from) params.append("date_from", date_from);
  if (date_to) params.append("date_to", date_to);

  const res = await fetch(`/data?${params}`);
  if (!res.ok) throw new Error(`Failed to fetch data: ${res.status}`);
  return res.json();
}

export async function triggerRefresh() {
  const res = await fetch("/refresh", { method: "POST" });
  if (!res.ok) throw new Error(`Refresh failed: ${res.status}`);
  return res.json();
}
