import React from 'react';
import { Cloud, Newspaper, Cpu } from 'lucide-react';

export default function DashboardTab({ weather, briefing, systemStats }) {
  const w = weather?.ok ? weather : null;
  const b = briefing?.ok ? briefing : null;
  const s = systemStats?.ok ? systemStats : null;

  return (
    <div className="flex-1 overflow-auto p-6 flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none mix-blend-overlay" />

      {/* Weather */}
      <section className="relative z-10 backdrop-blur-xl bg-black/30 border border-cyan-500/20 rounded-xl p-4 shadow-xl">
        <div className="flex items-center gap-2 mb-3 text-cyan-400">
          <Cloud size={20} />
          <h2 className="text-lg font-bold tracking-wider">Weather</h2>
        </div>
        {w ? (
          <div className="space-y-2 text-cyan-100/90">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-mono font-bold text-cyan-300">
                {w.current?.temperature_2m != null ? `${w.current.temperature_2m}°C` : '--'}
              </span>
              <span className="text-sm text-cyan-400/80">{w.current?.weather_label}</span>
            </div>
            <div className="text-sm flex flex-wrap gap-4">
              {w.current?.relative_humidity_2m != null && (
                <span>Humidity {w.current.relative_humidity_2m}%</span>
              )}
              {w.current?.wind_speed_10m != null && (
                <span>Wind {w.current.wind_speed_10m} km/h</span>
              )}
              {w.timezone && <span>{w.timezone}</span>}
            </div>
            {w.hourly?.length > 0 && (
              <div className="mt-3 pt-3 border-t border-cyan-500/20">
                <p className="text-xs text-cyan-500/70 mb-2">Next hours</p>
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {w.hourly.slice(0, 12).map((h, i) => (
                    <div
                      key={i}
                      className="shrink-0 text-center px-2 py-1 rounded bg-cyan-900/20 border border-cyan-500/10"
                    >
                      <div className="text-[10px] text-cyan-500/80">
                        {h.time ? new Date(h.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--'}
                      </div>
                      <div className="text-sm font-mono">{h.temperature_2m != null ? `${h.temperature_2m}°` : '--'}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-cyan-600/80 text-sm">{weather?.error || 'Loading weather…'}</p>
        )}
      </section>

      {/* Daily Briefing */}
      <section className="relative z-10 backdrop-blur-xl bg-black/30 border border-cyan-500/20 rounded-xl p-4 shadow-xl">
        <div className="flex items-center gap-2 mb-3 text-cyan-400">
          <Newspaper size={20} />
          <h2 className="text-lg font-bold tracking-wider">Daily Briefing</h2>
        </div>
        {b ? (
          <div className="space-y-3 text-cyan-100/90 text-sm">
            {['technology', 'science', 'top'].map((cat) => {
              const items = b.headlines?.[cat] || [];
              if (items.length === 0) return null;
              return (
                <div key={cat}>
                  <p className="text-cyan-500/80 text-xs uppercase tracking-wider mb-1">{cat}</p>
                  <ul className="space-y-1">
                    {items.slice(0, 5).map((item, i) => (
                      <li key={i}>
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-cyan-300/90 hover:text-cyan-200 hover:underline truncate block"
                        >
                          {item.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
            {b.summary && (
              <p className="text-cyan-400/80 text-xs mt-2 pt-2 border-t border-cyan-500/20">{b.summary}</p>
            )}
          </div>
        ) : (
          <p className="text-cyan-600/80 text-sm">{briefing?.error || 'Loading briefing…'}</p>
        )}
      </section>

      {/* System Monitor */}
      <section className="relative z-10 backdrop-blur-xl bg-black/30 border border-cyan-500/20 rounded-xl p-4 shadow-xl">
        <div className="flex items-center gap-2 mb-3 text-cyan-400">
          <Cpu size={20} />
          <h2 className="text-lg font-bold tracking-wider">System</h2>
        </div>
        {s ? (
          <div className="space-y-3 text-cyan-100/90 text-sm">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>CPU</span>
                <span>{s.cpu_percent?.toFixed(1) ?? 0}%</span>
              </div>
              <div className="h-2 rounded-full bg-cyan-900/40 overflow-hidden">
                <div
                  className="h-full bg-cyan-500/70 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, s.cpu_percent ?? 0)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Memory</span>
                <span>{s.memory_used_gb ?? 0} / {s.memory_total_gb ?? 0} GB ({s.memory_percent?.toFixed(1) ?? 0}%)</span>
              </div>
              <div className="h-2 rounded-full bg-cyan-900/40 overflow-hidden">
                <div
                  className="h-full bg-cyan-500/70 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, s.memory_percent ?? 0)}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <p className="text-cyan-600/80 text-sm">{systemStats?.error || 'Loading system stats…'}</p>
        )}
      </section>
    </div>
  );
}
