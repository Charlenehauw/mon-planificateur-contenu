# 🚀 Guide de déploiement — Planificateur Contenu IA

## Ce que tu vas faire
Héberger ton appli gratuitement sur Vercel en ~20 minutes, avec ta clé API sécurisée.

---

## ÉTAPE 1 — Installer Node.js

1. Va sur https://nodejs.org
2. Clique sur le bouton vert **"LTS"** (la version stable)
3. Télécharge et installe (clique sur Suivant à chaque étape)
4. ✅ Node.js est installé

---

## ÉTAPE 2 — Créer un compte GitHub

1. Va sur https://github.com
2. Clique **Sign up** → entre ton email, un mot de passe, un pseudo
3. Confirme ton email
4. ✅ Compte GitHub créé

---

## ÉTAPE 3 — Mettre le projet sur GitHub

1. Connecte-toi sur https://github.com
2. Clique sur le **+** en haut à droite → **New repository**
3. Nom du repo : `mon-planificateur-contenu`
4. Laisse tout par défaut → clique **Create repository**
5. GitHub te montre une page avec des instructions

Ensuite, sur ton ordi :
- Ouvre **VS Code** (télécharge sur https://code.visualstudio.com si pas encore fait)
- Glisse le dossier `mon-planificateur` dans VS Code
- Dans VS Code, ouvre le **Terminal** : menu `Terminal` → `New Terminal`
- Tape ces commandes une par une (appuie sur Entrée après chaque) :

```
git init
git add .
git commit -m "premier commit"
git branch -M main
git remote add origin https://github.com/TON_PSEUDO/mon-planificateur-contenu.git
git push -u origin main
```

⚠️ Remplace `TON_PSEUDO` par ton pseudo GitHub

✅ Ton code est maintenant sur GitHub

---

## ÉTAPE 4 — Créer un compte Vercel

1. Va sur https://vercel.com
2. Clique **Sign Up** → choisis **Continue with GitHub**
3. Autorise Vercel à accéder à GitHub
4. ✅ Compte Vercel créé et lié à GitHub

---

## ÉTAPE 5 — Déployer sur Vercel

1. Sur Vercel, clique **Add New Project**
2. Tu vois ton repo `mon-planificateur-contenu` → clique **Import**
3. Laisse tous les paramètres par défaut
4. Clique **Deploy**
5. Vercel construit ton appli (1-2 minutes)
6. ✅ Tu as une URL du type `mon-planificateur-contenu.vercel.app`

---

## ÉTAPE 6 — Ajouter ta clé API (IMPORTANT 🔐)

C'est ici que ta clé reste cachée et sécurisée.

1. Va sur https://console.anthropic.com
2. Dans le menu, clique **API Keys** → **Create Key**
3. Copie la clé (elle commence par `sk-ant-...`)
4. Retourne sur Vercel → ton projet → onglet **Settings**
5. Dans le menu gauche : **Environment Variables**
6. Clique **Add New** :
   - **Name** : `ANTHROPIC_API_KEY`
   - **Value** : colle ta clé `sk-ant-...`
7. Clique **Save**
8. Va dans l'onglet **Deployments** → clique les **3 points** sur le dernier déploiement → **Redeploy**

✅ Ta clé est sécurisée et l'appli fonctionne !

---

## ÉTAPE 7 — Tester 🎉

Va sur ton URL Vercel → remplis le formulaire → génère du contenu !

---

## En cas de problème

- Le terminal affiche une erreur en rouge → copie le message et envoie-le moi
- L'appli s'affiche mais la génération ne marche pas → vérifie l'étape 6 (clé API)
- Page blanche → dans Vercel, onglet Deployments, clique sur ton déploiement pour voir les logs

---

## Partager l'appli à tes clients

Tu peux envoyer directement l'URL `mon-planificateur-contenu.vercel.app` à qui tu veux.
Pour un nom de domaine personnalisé (ex: `contenu.tonsite.fr`), c'est faisable dans Vercel → Settings → Domains.
