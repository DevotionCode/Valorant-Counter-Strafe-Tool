# Counter-Strafe Tool (Strafing Analyzer Pro)

**Counter-Strafe Tool** est une application d'overlay conçue pour aider les joueurs de FPS (comme CS2, Valorant) à perfectionner leur mécanique de "counter-strafing".

Le counter-strafing consiste à arrêter instantanément son mouvement latéral avant de tirer pour garantir une précision maximale. Cet outil visualise vos entrées clavier et souris en temps réel pour vous aider à synchroniser votre tir avec l'arrêt de votre mouvement.

## 🚀 Fonctionnalités Principales

*   **Timeline en Temps Réel** : Visualisez graphiquement vos appuis sur les touches de mouvement (Q/D) et vos clics de souris.
*   **Analyse de Latence** : Calcule le délai exact (en millisecondes) entre l'arrêt de votre mouvement et votre tir.
*   **Feedback Immédiat** :
    *   **Vert** : Tir valide (effectué après l'arrêt, sous le seuil défini).
    *   **Rouge** : Tir invalide (effectué pendant le mouvement ou trop tard).
*   **Statistiques de Session** : Affiche le nombre de tirs valides/invalides et votre pourcentage de réussite.
*   **Overlay Discret** : Fenêtre transparente "Always-on-top" qui se superpose à votre jeu sans gêner la vue.
*   **Seuil Personnalisable** : Ajustez la tolérance de délai (MS) selon votre niveau ou le jeu.

## 🛠 Installation et Utilisation

### Via l'exécutable (Recommandé)
1.  Téléchargez la dernière version depuis l'onglet **Releases**.
2.  Lancez `StrafingAnalyzerPro.exe`.
3.  Lancez votre jeu en mode "Fenêtré sans bordures" (Borderless Windowed) pour que l'overlay reste visible.

### Via Python (Développement)
1.  Clonez le dépôt.
2.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
3.  Lancez l'application :
    ```bash
    python main.py
    ```

## 🎮 Contrôles
*   **Q / D** : Touches de mouvement (Configuration AZERTY par défaut).
*   **Clic Gauche** : Tir.
*   **X (Haut Droit)** : Fermer l'application.
*   **Restart Session** : Réinitialiser les statistiques.
