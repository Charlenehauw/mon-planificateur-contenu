import { useState } from "react";

const Y = "#F5C518";
const SECTORS = [
  "Beauté & Bien-être","Événementiel","Juridique","Immobilier",
  "Coach / Développement perso","Mode & Lifestyle","Restaurant & Food",
  "Fitness & Sport","E-commerce","Freelance / Services","Autre"
];
const GOALS = [
  "Gagner en visibilité","Générer des leads","Fidéliser ma communauté",
  "Vendre un produit / service","Partager mon expertise","Humaniser ma marque"
];
const PLATFORMS = ["Instagram","LinkedIn","TikTok","Facebook","Threads"];
const TONES = ["Professionnel","Authentique","Inspirant","Éducatif","Humoristique"];
const PERSONAS = [
  { id:"f18", label:"Femme 18–25 ans", icon:"👩" },
  { id:"f26", label:"Femme 26–35 ans", icon:"👩‍💼" },
  { id:"f36", label:"Femme 36–50 ans", icon:"👩‍🦱" },
  { id:"h18", label:"Homme 18–25 ans", icon:"👨" },
  { id:"h26", label:"Homme 26–35 ans", icon:"👨‍💼" },
  { id:"h36", label:"Homme 36–50 ans", icon:"👨‍🦱" },
  { id:"couple", label:"Couple", icon:"👫" },
  { id:"entrepreneur", label:"Entrepreneur·e", icon:"🚀" },
  { id:"enfants", label:"Enfants", icon:"🧒" },
  { id:"parents", label:"Parents", icon:"👨‍👩‍👧" },
];
const DAYS = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"];

const Chip = ({ label, selected, onClick }) => (
  <button onClick={onClick} style={{
    padding:"8px 16px", borderRadius:"2px",
    border:`1px solid ${selected ? Y : "rgba(255,255,255,0.13)"}`,
    background: selected ? `${Y}18` : "transparent",
    color: selected ? Y : "rgba(255,255,255,0.45)",
    cursor:"pointer", fontSize:"13px",
    fontFamily:"'DM Sans', sans-serif",
    letterSpacing:"0.02em", transition:"all 0.18s", whiteSpace:"nowrap"
  }}>{label}</button>
);

const SectionLabel = ({ title }) => (
  <div style={{ display:"flex", alignItems:"center", gap:"12px", marginBottom:"14px" }}>
    <span style={{ display:"block", width:"24px", height:"1px", background:Y }} />
    <span style={{ fontSize:"10px", letterSpacing:"0.18em", color:Y,
      fontFamily:"'DM Sans', sans-serif", fontWeight:"600" }}>{title}</span>
  </div>
);

const fmtPalette = { Reels:Y, Carrousel:"#fff", Story:"#888", Post:Y, Citation:"#ccc", "Post photo":Y };
const getFmt = f => { for (const k in fmtPalette) if (f?.includes(k)) return fmtPalette[k]; return Y; };

export default function App() {
  const [sector, setSector] = useState("");
  const [customSector, setCustomSector] = useState("");
  const [goal, setGoal] = useState("");
  const [platform, setPlatform] = useState("");
  const [tone, setTone] = useState("");
  const [persona, setPersona] = useState("");
  const [mode, setMode] = useState("ideas");
  const [loading, setLoading] = useState(false);
  const [ideas, setIdeas] = useState(null);
  const [calendar, setCalendar] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(null);

  const activeSector = sector === "Autre" ? customSector : sector;
  const activePersona = PERSONAS.find(p => p.id === persona)?.label || "";
  const isReady = activeSector && goal && platform && tone && persona;

  const copy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  };

  const generate = async () => {
    if (!isReady) { setError("Merci de remplir tous les champs 😊"); return; }
    setError(""); setLoading(true); setIdeas(null); setCalendar(null);

    if (mode === "ideas") {
      const prompt = `Tu es expert en stratégie de contenu réseaux sociaux.

Génère 7 idées de posts pour :
- Secteur : ${activeSector}
- Objectif : ${goal}
- Plateforme : ${platform}
- Ton : ${tone}
- Persona cible : ${activePersona}

Règles importantes :
- Varie les formats : Reels, Carrousel, Citation, Story, Post photo
- Pour les Carrousels : fournis un tableau "slides" avec 4 à 6 titres de slides (ex: ["Slide 1 : intro", "Slide 2 : point clé", ...])
- Pour tous les autres formats : "slides" doit être un tableau vide []
- Chaque idée doit avoir un titre accrocheur ("angle"), une légende prête à publier avec émojis et CTA

Réponds UNIQUEMENT en JSON valide (tableau de 7 objets), sans texte avant ni après :
[{"format":"Reels ou Carrousel ou Citation ou Story ou Post photo","angle":"titre accrocheur en 1 ligne","description":"2-3 phrases sur le contenu à créer","slides":["Slide 1 : ...", "Slide 2 : ..."],"caption":"légende prête avec émojis et call-to-action max 120 mots","hashtags":"6 hashtags pertinents"}]`;

      try {
        const res = await fetch("/api/generate", {
          method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        const raw = data.content?.map(i=>i.text||"").join("").trim();
        setIdeas(JSON.parse(raw.replace(/```json|```/g,"").trim()));
      } catch { setError("Erreur lors de la génération. Réessaie 🔄"); }

    } else {
      const prompt = `Tu es expert en stratégie de contenu réseaux sociaux.

Génère un calendrier éditorial sur 4 semaines pour :
- Secteur : ${activeSector}
- Objectif : ${goal}
- Plateforme : ${platform}
- Ton : ${tone}
- Persona cible : ${activePersona}

Les week-ends (Sam et Dim) sont libres, ne génère du contenu que pour Lun Mar Mer Jeu Ven.

Réponds UNIQUEMENT en JSON valide, sans texte avant ni après :
{"weeks":[{"week":1,"days":[{"day":"Lun","theme":"thème court","format":"Reels ou Carrousel ou Story ou Post ou Citation","angle":"idée de post en 1 ligne"},{"day":"Mar",...},{"day":"Mer",...},{"day":"Jeu",...},{"day":"Ven",...}]},{"week":2,...},{"week":3,...},{"week":4,...}]}`;

      try {
        const res = await fetch("/api/generate", {
          method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        const raw = data.content?.map(i=>i.text||"").join("").trim();
        setCalendar(JSON.parse(raw.replace(/```json|```/g,"").trim()));
      } catch { setError("Erreur lors de la génération. Réessaie 🔄"); }
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight:"100vh", background:"#090909", fontFamily:"'DM Sans', sans-serif", color:"#fff" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        input{outline:none;}
        input::placeholder{color:rgba(255,255,255,0.22);}
        ::-webkit-scrollbar{width:3px;}
        ::-webkit-scrollbar-track{background:#111;}
        ::-webkit-scrollbar-thumb{background:#2a2a2a;}
        button:focus{outline:none;}
      `}</style>

      {/* Header */}
      <div style={{ borderBottom:"1px solid rgba(255,255,255,0.06)", padding:"18px 32px",
        display:"flex", alignItems:"center", justifyContent:"space-between" }}>
        <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
          <div style={{ width:"7px", height:"7px", background:Y }} />
          <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:"19px",
            fontWeight:"400", letterSpacing:"0.06em" }}>Contenu IA</span>
        </div>
        <span style={{ fontSize:"10px", color:"rgba(255,255,255,0.2)", letterSpacing:"0.16em" }}>
          PLANIFICATEUR INTELLIGENT
        </span>
      </div>

      <div style={{ maxWidth:"820px", margin:"0 auto", padding:"52px 24px 80px" }}>

        {/* Hero */}
        <div style={{ marginBottom:"52px" }}>
          <h1 style={{ fontFamily:"'Cormorant Garamond',serif", fontWeight:"300",
            fontSize:"clamp(38px,5.5vw,62px)", lineHeight:"1.1", marginBottom:"18px" }}>
            Dis-moi qui tu cibles,<br />
            <em style={{ color:Y, fontStyle:"italic" }}>je te dis quoi poster.</em>
          </h1>
          <p style={{ color:"rgba(255,255,255,0.35)", fontSize:"15px", fontWeight:"300", maxWidth:"460px" }}>
            Idées de contenu sur-mesure ou calendrier éditorial complet — générés en quelques secondes.
          </p>
        </div>

        {/* Mode */}
        <div style={{ display:"flex", marginBottom:"44px", border:"1px solid rgba(255,255,255,0.1)",
          borderRadius:"2px", overflow:"hidden", width:"fit-content" }}>
          {[["ideas","✦  Idées de posts"],["calendar","▦  Calendrier 4 semaines"]].map(([m,l]) => (
            <button key={m} onClick={() => { setMode(m); setIdeas(null); setCalendar(null); }} style={{
              padding:"13px 26px", border:"none", cursor:"pointer",
              background: mode===m ? Y : "transparent",
              color: mode===m ? "#0a0a0a" : "rgba(255,255,255,0.35)",
              fontSize:"13px", fontWeight: mode===m ? "600" : "400",
              fontFamily:"'DM Sans',sans-serif", letterSpacing:"0.05em", transition:"all 0.2s"
            }}>{l}</button>
          ))}
        </div>

        {/* Form */}
        <div style={{ background:"#111", border:"1px solid rgba(255,255,255,0.06)",
          borderRadius:"3px", padding:"36px 40px", marginBottom:"24px" }}>

          {/* Sector */}
          <div style={{ marginBottom:"30px" }}>
            <SectionLabel title="SECTEUR D'ACTIVITÉ" />
            <div style={{ display:"flex", flexWrap:"wrap", gap:"8px" }}>
              {SECTORS.map(s => <Chip key={s} label={s} selected={sector===s} onClick={() => setSector(s)} />)}
            </div>
            {sector==="Autre" && (
              <input value={customSector} onChange={e => setCustomSector(e.target.value)}
                placeholder="Précise ton secteur..."
                style={{ marginTop:"12px", width:"100%", padding:"12px 16px",
                  background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.1)",
                  color:"#fff", fontSize:"14px", fontFamily:"'DM Sans',sans-serif", borderRadius:"2px" }} />
            )}
          </div>

          {/* Persona */}
          <div style={{ marginBottom:"30px" }}>
            <SectionLabel title="PERSONA CIBLE" />
            <div style={{ display:"flex", flexWrap:"wrap", gap:"8px" }}>
              {PERSONAS.map(p => (
                <Chip key={p.id} label={`${p.icon}  ${p.label}`} selected={persona===p.id} onClick={() => setPersona(p.id)} />
              ))}
            </div>
          </div>

          {/* Grid: goal + platform + tone */}
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"32px" }}>
            <div>
              <SectionLabel title="OBJECTIF" />
              <div style={{ display:"flex", flexDirection:"column", gap:"6px" }}>
                {GOALS.map(g => (
                  <button key={g} onClick={() => setGoal(g)} style={{
                    padding:"10px 14px", textAlign:"left",
                    border:`1px solid ${goal===g ? Y : "rgba(255,255,255,0.07)"}`,
                    background: goal===g ? `${Y}12` : "transparent",
                    color: goal===g ? Y : "rgba(255,255,255,0.4)",
                    cursor:"pointer", fontSize:"13px", fontFamily:"'DM Sans',sans-serif",
                    borderRadius:"2px", transition:"all 0.15s"
                  }}>{g}</button>
                ))}
              </div>
            </div>
            <div>
              <div style={{ marginBottom:"28px" }}>
                <SectionLabel title="PLATEFORME" />
                <div style={{ display:"flex", flexWrap:"wrap", gap:"7px" }}>
                  {PLATFORMS.map(p => <Chip key={p} label={p} selected={platform===p} onClick={() => setPlatform(p)} />)}
                </div>
              </div>
              <div>
                <SectionLabel title="TON DE VOIX" />
                <div style={{ display:"flex", flexWrap:"wrap", gap:"7px" }}>
                  {TONES.map(t => <Chip key={t} label={t} selected={tone===t} onClick={() => setTone(t)} />)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div style={{ background:"rgba(255,70,70,0.08)", border:"1px solid rgba(255,70,70,0.2)",
            padding:"14px 18px", borderRadius:"2px", color:"#ff7070", fontSize:"13px", marginBottom:"18px" }}>
            {error}
          </div>
        )}

        <button onClick={generate} disabled={loading || !isReady} style={{
          width:"100%", padding:"18px",
          border:`1px solid ${isReady && !loading ? Y : "rgba(255,255,255,0.08)"}`,
          background: isReady && !loading ? Y : "transparent",
          color: isReady && !loading ? "#090909" : "rgba(255,255,255,0.18)",
          cursor: isReady && !loading ? "pointer" : "not-allowed",
          fontSize:"13px", fontWeight:"600", letterSpacing:"0.1em",
          fontFamily:"'DM Sans',sans-serif", borderRadius:"2px", transition:"all 0.2s"
        }}>
          {loading ? "GÉNÉRATION EN COURS…"
            : mode==="ideas" ? "GÉNÉRER MES IDÉES DE CONTENU"
            : "GÉNÉRER MON CALENDRIER ÉDITORIAL"}
        </button>

        {/* Results — Ideas */}
        {ideas && (
          <div style={{ marginTop:"56px" }}>
            <div style={{ display:"flex", alignItems:"center", gap:"14px", marginBottom:"32px" }}>
              <span style={{ display:"block", width:"44px", height:"1px", background:Y }} />
              <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:"24px",
                fontWeight:"300", fontStyle:"italic" }}>Tes {ideas.length} idées de contenu</span>
            </div>
            {ideas.map((item, i) => {
              const fc = getFmt(item.format);
              const isCarousel = item.format?.toLowerCase().includes("carrousel");
              const hasSlides = isCarousel && Array.isArray(item.slides) && item.slides.length > 0;
              const copyText = hasSlides
                ? `${item.angle}\n\nSLIDES :\n${item.slides.map((s,n) => `${n+1}. ${s}`).join("\n")}\n\nLÉGENDE :\n${item.caption}\n\n${item.hashtags}`
                : `${item.angle}\n\n${item.caption}\n\n${item.hashtags}`;
              return (
                <div key={i} style={{ marginBottom:"14px", border:"1px solid rgba(255,255,255,0.07)",
                  borderLeft:`3px solid ${fc}`, borderRadius:"2px", overflow:"hidden" }}>

                  {/* Header */}
                  <div style={{ padding:"26px 30px", borderBottom:"1px solid rgba(255,255,255,0.05)" }}>
                    <div style={{ display:"flex", gap:"12px", alignItems:"center", marginBottom:"10px" }}>
                      <span style={{ fontSize:"9px", letterSpacing:"0.16em", color:fc, fontWeight:"700" }}>
                        {item.format?.toUpperCase()}
                      </span>
                      <span style={{ fontSize:"9px", color:"rgba(255,255,255,0.18)" }}>#{i+1}</span>
                    </div>
                    <h3 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:"21px",
                      fontWeight:"400", lineHeight:"1.3", marginBottom:"10px" }}>{item.angle}</h3>
                    <p style={{ color:"rgba(255,255,255,0.42)", fontSize:"14px",
                      lineHeight:"1.75", fontWeight:"300" }}>{item.description}</p>
                  </div>

                  {/* Slides (carrousel only) */}
                  {hasSlides && (
                    <div style={{ padding:"20px 30px", borderBottom:"1px solid rgba(255,255,255,0.05)",
                      background:"rgba(245,197,24,0.03)" }}>
                      <div style={{ fontSize:"9px", letterSpacing:"0.14em",
                        color:Y, marginBottom:"12px", fontWeight:"600" }}>
                        STRUCTURE DES SLIDES
                      </div>
                      <div style={{ display:"flex", flexDirection:"column", gap:"6px" }}>
                        {item.slides.map((slide, si) => (
                          <div key={si} style={{ display:"flex", gap:"12px", alignItems:"flex-start" }}>
                            <span style={{ width:"20px", height:"20px", background:`${Y}22`,
                              color:Y, display:"flex", alignItems:"center", justifyContent:"center",
                              fontSize:"10px", fontWeight:"700", flexShrink:0, borderRadius:"2px" }}>
                              {si+1}
                            </span>
                            <span style={{ fontSize:"13px", color:"rgba(255,255,255,0.6)",
                              fontWeight:"300", lineHeight:"1.5", paddingTop:"2px" }}>{slide}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Caption */}
                  <div style={{ padding:"20px 30px", background:"rgba(255,255,255,0.015)" }}>
                    <div style={{ fontSize:"9px", letterSpacing:"0.14em",
                      color:"rgba(255,255,255,0.22)", marginBottom:"8px" }}>LÉGENDE</div>
                    <p style={{ color:"rgba(255,255,255,0.65)", fontSize:"14px",
                      lineHeight:"1.8", marginBottom:"16px", fontWeight:"300" }}>{item.caption}</p>
                    <div style={{ display:"flex", justifyContent:"space-between",
                      alignItems:"center", flexWrap:"wrap", gap:"10px" }}>
                      <span style={{ color:"rgba(255,255,255,0.22)", fontSize:"12px" }}>{item.hashtags}</span>
                      <button onClick={() => copy(copyText, i)} style={{
                        padding:"8px 20px",
                        border:`1px solid ${copied===i ? Y : "rgba(255,255,255,0.12)"}`,
                        background: copied===i ? `${Y}14` : "transparent",
                        color: copied===i ? Y : "rgba(255,255,255,0.35)",
                        cursor:"pointer", fontSize:"11px", letterSpacing:"0.08em",
                        fontFamily:"'DM Sans',sans-serif", borderRadius:"2px", transition:"all 0.2s"
                      }}>{copied===i ? "✓ COPIÉ" : "TOUT COPIER"}</button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Results — Calendar */}
        {calendar && (
          <div style={{ marginTop:"56px" }}>
            <div style={{ display:"flex", alignItems:"center", gap:"14px", marginBottom:"8px" }}>
              <span style={{ display:"block", width:"44px", height:"1px", background:Y }} />
              <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:"24px",
                fontWeight:"300", fontStyle:"italic" }}>Calendrier éditorial — 4 semaines</span>
            </div>
            <p style={{ color:"rgba(255,255,255,0.25)", fontSize:"12px", marginBottom:"36px", paddingLeft:"58px" }}>
              {activeSector} · {activePersona} · {platform}
            </p>

            {calendar.weeks?.map(week => (
              <div key={week.week} style={{ marginBottom:"36px" }}>
                <div style={{ display:"flex", alignItems:"center", gap:"14px", marginBottom:"14px" }}>
                  <div style={{ width:"30px", height:"30px", background:Y, color:"#090909",
                    display:"flex", alignItems:"center", justifyContent:"center",
                    fontSize:"12px", fontWeight:"700", flexShrink:0 }}>{week.week}</div>
                  <span style={{ fontSize:"10px", letterSpacing:"0.16em", color:"rgba(255,255,255,0.28)" }}>
                    SEMAINE {week.week}
                  </span>
                </div>

                <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:"6px" }}>
                  {DAYS.map((d, di) => {
                    const isWeekend = di >= 5;
                    const dayData = isWeekend ? null : week.days?.find(x => x.day === d) || week.days?.[di];
                    const fc = dayData ? getFmt(dayData.format) : "transparent";
                    return (
                      <div key={d} style={{
                        border:`1px solid ${isWeekend ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.09)"}`,
                        borderTop: isWeekend ? "1px solid rgba(255,255,255,0.04)" : `2px solid ${fc}`,
                        borderRadius:"2px", padding:"12px 10px",
                        background: isWeekend ? "rgba(255,255,255,0.01)" : "rgba(255,255,255,0.025)",
                        minHeight:"115px"
                      }}>
                        <div style={{ fontSize:"9px", letterSpacing:"0.12em", fontWeight:"600", marginBottom:"8px",
                          color: isWeekend ? "rgba(255,255,255,0.18)" : "rgba(255,255,255,0.45)" }}>{d}</div>
                        {dayData && (
                          <>
                            <div style={{ fontSize:"9px", color:fc, letterSpacing:"0.1em",
                              marginBottom:"6px", fontWeight:"600" }}>
                              {dayData.format?.toUpperCase()}
                            </div>
                            <div style={{ fontSize:"11px", color:"rgba(255,255,255,0.52)",
                              lineHeight:"1.55", fontWeight:"300" }}>{dayData.angle}</div>
                          </>
                        )}
                        {isWeekend && (
                          <div style={{ fontSize:"10px", color:"rgba(255,255,255,0.13)", fontStyle:"italic" }}>repos</div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            <button onClick={() => {
              const txt = calendar.weeks?.map(w =>
                `SEMAINE ${w.week}\n` + w.days?.map(d=>`${d.day} — [${d.format}] ${d.angle}`).join("\n")
              ).join("\n\n");
              copy(txt, "cal");
            }} style={{
              padding:"13px 28px",
              border:`1px solid ${copied==="cal" ? Y : "rgba(255,255,255,0.12)"}`,
              background: copied==="cal" ? `${Y}14` : "transparent",
              color: copied==="cal" ? Y : "rgba(255,255,255,0.35)",
              cursor:"pointer", fontSize:"11px", letterSpacing:"0.09em",
              fontFamily:"'DM Sans',sans-serif", borderRadius:"2px", transition:"all 0.2s"
            }}>{copied==="cal" ? "✓ CALENDRIER COPIÉ" : "COPIER TOUT LE CALENDRIER"}</button>
          </div>
        )}

        {(ideas || calendar) && (
          <button onClick={() => { setIdeas(null); setCalendar(null); setError(""); }} style={{
            marginTop:"20px", width:"100%", padding:"14px",
            border:"1px solid rgba(255,255,255,0.07)", background:"transparent",
            color:"rgba(255,255,255,0.2)", cursor:"pointer",
            fontSize:"11px", letterSpacing:"0.1em",
            fontFamily:"'DM Sans',sans-serif", borderRadius:"2px"
          }}>↺  RECOMMENCER</button>
        )}

        <div style={{ marginTop:"64px", borderTop:"1px solid rgba(255,255,255,0.05)",
          paddingTop:"20px", display:"flex", justifyContent:"space-between",
          fontSize:"10px", color:"rgba(255,255,255,0.15)", letterSpacing:"0.06em" }}>
          <span>Contenu IA — Planificateur intelligent</span>
          <span>Propulsé par Claude</span>
        </div>
      </div>
    </div>
  );
}
