export default function Home() {
  return (
    <main style={{ minHeight: '100vh', background: '#08090b', color: '#f5f7fa', padding: 40, fontFamily: 'Arial, sans-serif' }}>
      <section style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ opacity: 0.6, letterSpacing: 3, fontSize: 12 }}>KANA SOVEREIGN CORE</div>
        <h1 style={{ fontSize: 48, margin: '18px 0 8px' }}>BIG BRAIN</h1>
        <p style={{ opacity: 0.7, maxWidth: 700 }}>Vercel-native control plane for KANA. External services remain connectors; the cognitive core stays under KANA control.</p>
        <div style={{ marginTop: 36, display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(210px,1fr))', gap: 14 }}>
          {['Big Brain', 'Information Governor', 'Memory', 'Experience', 'Execution', 'Evolution'].map((item) => (
            <div key={item} style={{ border: '1px solid #24272d', padding: 22, borderRadius: 10, background: '#0e1014' }}>
              <div style={{ fontSize: 11, opacity: 0.5, letterSpacing: 2 }}>SYSTEM</div>
              <div style={{ marginTop: 10, fontSize: 18 }}>{item}</div>
              <div style={{ marginTop: 14, fontSize: 11, opacity: 0.5 }}>INITIALIZING</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
