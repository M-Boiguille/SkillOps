# ⌨️ Keybindings - SkillOps CLI

## Navigation dans le Menu

### Méthode Standard
- `↑` (Flèche Haut) : Monter dans la liste
- `↓` (Flèche Bas) : Descendre dans la liste
- `Enter` : Sélectionner l'option
- `Ctrl+C` : Quitter

### Méthode Vim (style vi/vim)
- `k` : Monter dans la liste (équivalent à ↑)
- `j` : Descendre dans la liste (équivalent à ↓)
- `Enter` : Sélectionner l'option
- `Ctrl+C` : Quitter

## Exemples d'Utilisation

### Navigation Classique
```
python skillops.py start
[Utiliser ↑↓ pour naviguer]
[Appuyer sur Enter pour sélectionner]
```

### Navigation Vim
```
python skillops.py start
[Utiliser j/k pour naviguer]
  j = descendre (down)
  k = monter (up)
[Appuyer sur Enter pour sélectionner]
```

## Fonctionnalités

- ✅ **Carousel mode** : Navigation circulaire (retour au début/fin)
- ✅ **Highlight visuel** : Sélection en couleur cyan
- ✅ **Support multi-méthode** : Flèches ET vim simultanément
- ✅ **Interruption propre** : Ctrl+C sort proprement du menu

## Tips

1. **Pour les utilisateurs Vim** : Utilisez `j`/`k` naturellement
2. **Pour les débutants** : Les flèches fonctionnent toujours
3. **Navigation rapide** : Le mode carousel permet de boucler
4. **Muscle memory** : Les deux méthodes peuvent être mélangées

## Implémentation Technique

Le support vim est implémenté via un monkey patch d'inquirer :

```python
# src/lms/cli.py
def vim_aware_process_input(self, pressed):
    """Process input with vim keybindings support (j=down, k=up)."""
    if pressed == "j":
        pressed = readchar.key.DOWN
    elif pressed == "k":
        pressed = readchar.key.UP
    return original_process_input(self, pressed)
```

Cette méthode traduit `j`/`k` en événements de flèches directionnelles avant le traitement par inquirer.

## Compatibilité

- ✅ Linux : Testé sur Ubuntu/Debian
- ✅ macOS : Compatible
- ⚠️ Windows : Devrait fonctionner (non testé)

## Future Enhancements

- [ ] Support de `gg` pour aller au début
- [ ] Support de `G` pour aller à la fin
- [ ] Support de `/` pour recherche
- [ ] Support de `?` pour aide contextuelle
