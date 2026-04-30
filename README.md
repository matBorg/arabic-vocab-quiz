# 🧠 Arabic Flashcards Game

Un’app per imparare parole arabe in modo semplice e interattivo.

Include:

* 🎯 Quiz a risposta multipla
* 🧠 Ripasso intelligente
* 📊 Statistiche progresso

---




---

# 📁 Struttura del progetto

```id="structure1"
project/
│
├── app.py
├── data/              ← parole arabe (JSON)
├── progress.json      ← salva i tuoi progressi
└── README.md
```

---

# 📚 Come aggiungere nuove lezioni

Le parole si trovano nella cartella:

```id="datafolder"
data/
```

Ogni file è una “sessione di studio”.

---

## 📄 Formato file JSON

Esempio:

```json id="json1"
[
  {
    "arabic": "كِتَاب",
    "correct": "libro",
    "options": ["libro", "casa", "porta", "penna"]
  }
]
```

---

## 📌 Regole

* `"arabic"` → parola in arabo
* `"correct"` → risposta giusta
* `"options"` → 4 risposte totali
* Solo UNA deve essere corretta

---

# 🤖 Generare nuove sessioni automaticamente

Puoi usare ChatGPT con questo prompt:

---

## 🧠 PROMPT

```id="prompt1"
Prendi il testo che ti fornisco e individua tutte le parole nuove (lessico).

Per ogni parola crea una flashcard in formato JSON con questa struttura:

{
  "arabic": "...",
  "correct": "...",
  "options": ["...", "...", "...", "..."]
}



"arabic" → parola in arabo
"correct" → risposta giusta (in italiano)
"options" → 4 risposte totali possibili (in italiano)
Solo UNA deve essere corretta


Requisiti:
- L’arabo deve includere gli harakat
- Solo una risposta deve essere corretta
- Le altre opzioni devono essere plausibili
- Output finale deve essere JSON valido

Testo:
[INCOLLA QUI IL TESTO]
```

---

# 🧠 Come funziona il gioco

## 🎯 Quiz

* ti viene mostrata una parola araba
* scegli la traduzione corretta

---

## 🧠 Ripasso intelligente

* il gioco ricorda i tuoi errori
* ti propone più spesso le parole difficili

---

# 📊 Progresso

Il file:

```id="progress"
progress.json
```

serve per:

* salvare errori
* migliorare il ripasso
* tracciare le parole viste

---