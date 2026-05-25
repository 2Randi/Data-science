# Guide de configuration SSH pour GitLab
<div align="right">

[← Retour à la documentation principale](../README.md)

</div>

## Résolution des problèmes d'authentification SSH

### 1. Vérification des clés SSH existantes
```bash
ls -al ~/.ssh
```

### 2. Création d'une nouvelle clé SSH
```bash
ssh-keygen -t ed25519 -C "votre_email@exemple.com"
```
- Appuyez sur **Entrée** pour le chemin de sauvegarde par défaut
- Choisissez un mot de passe (optionnel mais recommandé)

### 3. Copie de la clé publique
```bash
# macOS
cat ~/.ssh/id_ed25519.pub | pbcopy

# Linux
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard
```

### 4. Ajout de la clé à GitLab

1. **Connectez-vous** à votre compte GitLab
2. **Cliquez sur votre photo de profil** en haut à droite
3. Sélectionnez **"Edit profile"** dans le menu déroulant
4. Dans le menu de gauche, cliquez sur **"SSH Keys"**
5. Collez la clé que vous avez copiée dans la zone de texte **"Key"**
6. Laissez le **"Title"** se remplir automatiquement ou donnez un nom reconnaissable
7. **Cliquez sur le bouton "Add key"**

**Alternative :** Si vous ne trouvez pas cette option, vous pouvez aussi utiliser les **Project Access Tokens** :

1. Allez dans votre projet
2. **Settings** → **Access Tokens**
3. Créez un nouveau token avec les scopes `read_repository` et `write_repository`
4. Utilisez-le pour cloner avec HTTPS :
```bash
git clone https://oauth2:VOTRE_TOKEN@gitlab.etu.umontpellier.fr/utilisateur/depot.git
```
### 5. Test de la connexion
```bash
ssh -T git@gitlab.etu.umontpellier.fr
```

### 6. Clonage du dépôt
```bash
git clone git@gitlab.etu.umontpellier.fr:utilisateur/nom-du-depot.git
```

## Solutions alternatives

### Méthode HTTPS
```bash
git clone https://gitlab.etu.umontpellier.fr/utilisateur/nom-du-depot.git
```

### Configuration Git de base
```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre_email@exemple.com"
```

## Dépannage avancé

### Création d'une clé sans mot de passe
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_gitlab -C "votre_email@exemple.com"
```

### Ajout au SSH Agent
```bash
ssh-add ~/.ssh/id_ed25519
```

## Notes importantes
- L'authentification SSH est plus sécurisée que HTTPS
- Les clés SSH n'expirent pas (contrairement aux tokens)
- Conservez votre clé privée en sécurité