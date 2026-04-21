<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WinScreen - Présentation Officielle</title>
    <style>
        :root {
            --primary: #00ff41;
            --bg: #0d0d0d;
            --card-bg: #1a1a1a;
            --text: #ffffff;
            --secondary: #008f11;
            --code-bg: #000000;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        .hero {
            background: linear-gradient(180deg, #1a1a1a 0%, var(--bg) 100%);
            padding: 80px 20px;
            text-align: center;
            border-bottom: 2px solid var(--primary);
        }

        .title {
            font-size: 3.5rem;
            margin: 0;
            color: var(--primary);
            text-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
        }

        .badge-container {
            margin: 20px 0;
        }

        .badge {
            display: inline-block;
            padding: 5px 15px;
            margin: 5px;
            border-radius: 5px;
            font-size: 0.8rem;
            font-weight: bold;
            background: var(--card-bg);
            border: 1px solid #333;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        h2 {
            color: var(--primary);
            border-left: 4px solid var(--primary);
            padding-left: 15px;
            margin-top: 50px;
            text-transform: uppercase;
        }

        /* Section Caractéristiques */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .feature-card {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
            transition: 0.3s;
        }

        .feature-card:hover {
            border-color: var(--primary);
            transform: translateY(-5px);
        }

        .icon { font-size: 2rem; margin-bottom: 10px; display: block; }

        /* Section Installation */
        .code-block {
            background: var(--code-bg);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--secondary);
            position: relative;
            margin: 20px 0;
        }

        code {
            font-family: 'Consolas', 'Monaco', monospace;
            color: var(--primary);
        }

        .step {
            margin-bottom: 30px;
        }

        /* Section Dépendances / Table */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: var(--card-bg);
        }

        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #333;
        }

        th { color: var(--primary); }

        footer {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 0.9rem;
        }

        .highlight { color: var(--primary); font-weight: bold; }
    </style>
</head>
<body>

    <header class="hero">
        <h1 class="title">🖥️ WinScreen</h1>
        <p>L'alternative moderne et libre pour la capture Windows</p>
        <div class="badge-container">
            <span class="badge" style="border-color: #3776ab;">Python 3.9+</span>
            <span class="badge" style="border-color: #f1c40f;">License MIT</span>
            <span class="badge" style="border-color: #e67e22;">CustomTkinter UI</span>
        </div>
        <p style="max-width: 600px; margin: 20px auto; color: #aaa;">
            Développé pour pallier les limitations de l'outil système, notamment sur les versions de Windows non activées.
        </p>
    </header>

    <div class="container">
        
        <section id="features">
            <h2>✨ Caractéristiques</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <span class="icon">📸</span>
                    <h3>Capture Ultra-Rapide</h3>
                    <p>Screenshots instantanés sans latence grâce au moteur <span class="highlight">mss</span>.</p>
                </div>
                <div class="feature-card">
                    <span class="icon">🎥</span>
                    <h3>Enregistrement Vidéo</h3>
                    <p>Capturez votre activité écran en haute fluidité pour vos tutoriels ou audits.</p>
                </div>
                <div class="feature-card">
                    <span class="icon">🎨</span>
                    <h3>Interface Cyber</h3>
                    <p>Design sombre et moderne utilisant <span class="highlight">CustomTkinter</span>.</p>
                </div>
                <div class="feature-card">
                    <span class="icon">🆓</span>
                    <h3>Zéro Restriction</h3>
                    <p>Fonctionne sans Windows activé. Votre matériel, vos règles.</p>
                </div>
            </div>
        </section>

        <section id="installation">
            <h2>🛠️ Installation & Prérequis</h2>
            
            <div class="step">
                <h3>1. Prérequis Système</h3>
                <p>Python 3.9 ou supérieur est requis pour exécuter WinScreen.</p>
            </div>

            <div class="step">
                <h3>2. Dépendances requises</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Librairie</th>
                            <th>Utilité</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>customtkinter</code></td>
                            <td>Interface utilisateur moderne et réactive.</td>
                        </tr>
                        <tr>
                            <td><code>Pillow</code></td>
                            <td>Traitement et sauvegarde des images.</td>
                        </tr>
                        <tr>
                            <td><code>mss</code></td>
                            <td>Capture d'écran haute performance (multi-écrans).</td>
                        </tr>
                        <tr>
                            <td><code>pywin32</code></td>
                            <td>Interaction avec les API natives de Windows.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="step">
                <h3>3. Installation Rapide</h3>
                <p>Exécutez ces commandes dans votre terminal :</p>
                <div class="code-block">
                    <code>
                        git clone https://github.com/votre-utilisateur/winscreen.git<br>
                        cd winscreen<br>
                        pip install -r requirements.txt<br>
                        python main.py
                    </code>
                </div>
            </div>
        </section>

        <section id="usage">
            <h2>🚀 Utilisation</h2>
            <ul>
                <li>Lancer l'application via <span class="highlight">main.py</span> ou l'exécutable.</li>
                <li>Sélectionner le mode (Image ou Vidéo).</li>
                <li>Définir la zone de capture.</li>
                <li>Retrouver vos fichiers dans le dossier <code>data/captures/</code>.</li>
            </ul>
        </section>

    </div>

    <footer>
        <p>WinScreen - Développé avec passion pour la liberté logicielle.</p>
        <p style="font-size: 0.7rem;">&copy; 2026 WinScreen Project</p>
    </footer>

</body>
</html>
