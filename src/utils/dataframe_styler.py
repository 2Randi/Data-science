from itertools import cycle
import pandas as pd
import re


def natural_sort_key(text):
    """
    تابع برای تبدیل متن به کلیدی که برای مرتب‌سازی طبیعی استفاده میشه
    مثال: C1, C2, C10 به جای C1, C10, C2
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', str(text))]


class DataFrameStyler:
    """
    Classe pour styliser les lignes dupliquées dans un DataFrame avec des couleurs alternées
    
    Exemples d'utilisation:
    
    1. Utilisation simple avec la fonction (recommandée):
       >>> from utils.dataframe_styler import style_duplicates
       >>> styled_df = style_duplicates(df)
       >>> display(styled_df)
    
    2. Avec une colonne ID personnalisée:
       >>> style_duplicates(df, id_column='order_id')
    
    3. Avec des couleurs personnalisées:
       >>> style_duplicates(df, colors=['#FFE6E6', '#E6F3FF'])
    
    4. Avec tous les paramètres:
       >>> style_duplicates(df, id_column='client_id', colors=['#FFEAA7', '#DFE6E9'])
    
    5. Utilisation directe de la classe (alternative):
       >>> from utils.dataframe_styler import DataFrameStyler
       >>> styler = DataFrameStyler(df, id_column='user_id')
       >>> styled_result = styler.apply()
       >>> display(styled_result)
    
    6. Utilisation avec monkey patch (méthode DataFrame):
       >>> df.style_duplicates()
       >>> df.style_duplicates(id_column='order_id')
       >>> df.style_duplicates(colors=['#FFE6E6', '#E6F3FF'])

    7. Avec tri par colonne:
       >>> df.style_duplicates(sort='Client')
       >>> df.style_duplicates(id_column='order_id', sort='date')
       >>> df.style_duplicates(sort='diff_days', ascending=False)

    """
    
    def __init__(self, df, id_column=None, colors=None, highlight_mask=None, highlight_color=None):
        """
        Initialiser le DataFrameStyler (avec les nouveaux paramètres de surlignage)
        
        Paramètres:
        -----------
        df : pandas.DataFrame
            DataFrame principal à styliser
        id_column : str, par défaut=None
            Nom de la colonne pour identifier les enregistrements dupliqués
            Si None, utilise l'index
        colors : list of str, optionnel
            Liste de codes couleur hexadécimaux pour mettre en évidence les groupes dupliqués
            Par défaut: ['#E1F5FE', '#FFFFFF'] (bleu clair et blanc)
        highlight_mask : pandas.DataFrame ou pandas.Series (booléen), optionnel
            Masque booléen pour mettre en évidence les cellules (ex: df['col'] == 171)
        highlight_color : str, optionnel
            Couleur de fond pour le surlignage du masque (Défaut: '#FFCCCC' - Rouge clair)
        Exemples:
        ---------
        >>> # Exemple 1: Utilisation de base
        >>> styler = DataFrameStyler(df)
        >>> result = styler.apply()
        >>> display(result)
        
        >>> # Exemple 2: Avec paramètres personnalisés
        >>> styler = DataFrameStyler(df, id_column='order_id', colors=['#FFE6E6', '#E6FFE6'])
        >>> styled_result = styler.apply()
        >>> display(styled_result)
        
        >>> # Exemple 3: Avec trois couleurs alternées
        >>> styler = DataFrameStyler(df, id_column='user_id', colors=['#FFE6E6', '#E6F3FF', '#E6FFE6'])
        >>> display(styler.apply())
        """
        self.df = df.copy()
        self.id_column = id_column
        self.colors = colors if colors is not None else ['#E1F5FE', '#FFFFFF']
        self.color_map = {}
        self.custom_sort_applied = False

        self.highlight_mask = highlight_mask
        self.highlight_color = highlight_color if highlight_color is not None else '#FFCCCC' # Rouge clair par défaut
        
    def sort_by_column(self, column_name, ascending=True, numeric=True):
        """
        Trier le DataFrame par une colonne spécifique
        
        Paramètres:
        -----------
        column_name : str
            Nom de la colonne pour le tri
        ascending : bool, par défaut=True
            Ordre de tri (True: croissant, False: décroissant)
        numeric : bool, par défaut=False
            Si True, trie les valeurs numériquement même si elles sont des strings
            Exemple: ['C1', 'C2', 'C10'] au lieu de ['C1', 'C10', 'C2']
        
        Returns:
        --------
        DataFrameStyler
            Instance actuelle pour le chaînage des méthodes
        
        Raises:
        -------
        Affiche un message d'avertissement si la colonne n'existe pas
        
        Exemples:
        ---------
        >>> styler = DataFrameStyler(df)
        >>> styler.sort_by_column('Client').apply()
        
        >>> styler.sort_by_column('date', ascending=False).apply()
        
        >>> # Tri numérique pour les strings
        >>> styler.sort_by_column('Client', numeric=True).apply()
        
        >>> # Chaînage des méthodes
        >>> df_styled = DataFrameStyler(df).sort_by_column('amount', numeric=True).apply()
        >>> display(df_styled)
        """
        if column_name in self.df.columns:
            if numeric:
                # استفاده از natural_sort_key برای تر تیب صحیح
                self.df = self.df.sort_values(
                    by=column_name,
                    ascending=ascending,
                    key=lambda x: x.apply(natural_sort_key)
                )
            else:
                self.df = self.df.sort_values(by=column_name, ascending=ascending)
            self.custom_sort_applied = True
        else:
            print(f"Colonne '{column_name}' introuvable. Tri non effectué.")
        
        return self  # Pour permettre le chaînage des méthodes

    def _find_duplicates(self):
        """
        Trouver et trier les lignes dupliquées
        
        Cette méthode identifie les enregistrements dupliqués basés sur:
        - La colonne ID spécifiée (id_column) si fournie
        - L'index du DataFrame sinon
        
        Returns:
        --------
        pandas.DataFrame
            DataFrame contenant uniquement les lignes dupliquées, triées par id_column ou index
        
        Notes:
        ------
        - Les lignes non dupliquées ne sont pas incluses dans le résultat
        - Le DataFrame retourné est toujours trié par la colonne d'identification
        - Si id_column n'existe pas, la méthode bascule automatiquement sur l'index
        
        Exemples:
        ---------
        >>> styler = DataFrameStyler(df, id_column='order_id')
        >>> duplicates = styler._find_duplicates()
        >>> print(f"Nombre de lignes dupliquées: {len(duplicates)}")
        """
        if self.id_column is None:
            # Utiliser l'index pour identifier les doublons
            duplicate_mask = self.df.index.duplicated(keep=False)
            duplicate_rows = self.df[duplicate_mask]
            return duplicate_rows.sort_index()
        elif self.id_column in self.df.columns:
            duplicate_mask = self.df.duplicated(subset=[self.id_column], keep=False)
            duplicate_rows = self.df[duplicate_mask]
            return duplicate_rows.sort_values(self.id_column)
        else:
            print(f"Colonne '{self.id_column}' introuvable. Utilisation de l'index pour la détection des doublons.")
            duplicate_mask = self.df.index.duplicated(keep=False)
            duplicate_rows = self.df[duplicate_mask]
            return duplicate_rows.sort_index()
    
    def _create_color_map(self, df_to_style):
        """
        Créer un mappage de couleurs pour les lignes
        
        Cette méthode assigne une couleur à chaque ligne en fonction de son groupe dupliqué.
        Elle utilise un cycle de couleurs pour alterner les teintes et améliorer la lisibilité.
        
        Paramètres:
        -----------
        df_to_style : pandas.DataFrame
            DataFrame à styliser
        
        Comportement:
        -------------
        Cas 1 - Groupage par colonne ID:
            Si id_column est spécifiée et existe, les lignes du même groupe reçoivent la même couleur
            et les groupes alternent entre les couleurs fournies.
        
        Cas 2 - Coloration de lignes alternées:
            Si id_column n'est pas disponible, les lignes reçoivent alternativement les couleurs
            selon leur position dans le DataFrame.
        
        Notes:
        ------
        - Le mappage est stocké dans self.color_map avec les indices des lignes comme clés
        - Utilise itertools.cycle() pour boucler à travers les couleurs indéfiniment
        - Optimisé pour les DataFrames avec de nombreux groupes dupliqués
        
        Exemples:
        ---------
        >>> styler = DataFrameStyler(df, id_column='user_id', colors=['#FFE6E6', '#E6F3FF'])
        >>> duplicate_rows = styler._find_duplicates()
        >>> styler._create_color_map(duplicate_rows)
        >>> # self.color_map contient maintenant: {idx1: '#FFE6E6', idx2: '#FFE6E6', idx3: '#E6F3FF', ...}
        """
        colors_cycle = cycle(self.colors)
        
        if self.id_column is not None and self.id_column in df_to_style.columns and not df_to_style.empty:
            # Cas 1: Grouper par colonne ID
            groups = df_to_style.groupby(self.id_column)
            
            # Créer un mappage de couleurs pour chaque groupe dupliqué
            for group_id, group_df in groups:
                color = next(colors_cycle)
                for idx in group_df.index:
                    self.color_map[idx] = color
        else:
            # Cas 2: Appliquer des couleurs alternées basées sur les lignes
            for i, idx in enumerate(df_to_style.index):
                color = self.colors[i % len(self.colors)]
                self.color_map[idx] = color
    
    def _highlight_duplicate_groups(self, row):
        """
        Fonction interne pour mettre en évidence les lignes
        
        Applique une couleur de fond et une couleur de texte à toutes les cellules d'une ligne
        basée sur le mappage de couleurs créé dans _create_color_map().
        
        Paramètres:
        -----------
        row : pandas.Series
            Ligne du DataFrame à styliser (appelée par la méthode apply() avec axis=1)
        
        Returns:
        --------
        list
            Liste de styles CSS pour chaque cellule de la ligne
        
        Notes:
        ------
        - La couleur est déterminée par row.name (l'index de la ligne)
        - Utilise 'white' comme couleur par défaut si la ligne n'est pas dans color_map
        - Le texte est toujours noir (#000000) pour une meilleure lisibilité
        - Chaque cellule reçoit le même style CSS
        
        Exemples:
        ---------
        >>> styler = DataFrameStyler(df)
        >>> # Cette méthode est utilisée en interne par apply()
        >>> # Pas d'utilisation directe recommandée
        """
        color = self.color_map.get(row.name, 'white')
        return [f'background-color: {color}; color: #000000;' for _ in row]
    
    @staticmethod
    def _highlight_missing_cells(cell):
        """
        Fonction pour mettre en évidence les cellules avec des valeurs '???' ou NaN en jaune
        
        Cette méthode identifie les valeurs manquantes ou indéfinies et les met en évidence
        avec une couleur jaune pour faciliter leur identification.
        
        Paramètres:
        -----------
        cell : any
            Valeur de la cellule à vérifier
        
        Returns:
        --------
        str
            Style CSS pour la cellule (jaune si manquante, vide sinon)
        
        Conditions détectées:
        --------------------
        - '???' : Placeholder personnalisé pour les valeurs manquantes
        - pd.isna(cell) : Valeurs NaN, None, ou autres valeurs manquantes pandas
        
        Notes:
        ------
        - La méthode est statique car elle n'a pas besoin d'accéder aux attributs de l'instance
        - Le texte est toujours noir (#000000) pour une lisibilité maximale sur le fond jaune
        - S'applique à chaque cellule individuellement du DataFrame
        
        Exemples:
        ---------
        >>> # Utilisation en interne (pas d'appel direct)
        >>> styled_df.map(DataFrameStyler._highlight_missing_cells)
        
        >>> # Identification des valeurs manquantes
        >>> # '???' → 'background-color: yellow; color: #000000;'
        >>> # NaN → 'background-color: yellow; color: #000000;'
        >>> # 'data' → ''
        """
        if cell == '???' or pd.isna(cell):
            return 'background-color: yellow; color: #000000;'
        return ''
    

    def _highlight_by_mask(self, data):
        """
        Fonction pour mettre en évidence les cellules basées sur un masque booléen.

        Cette méthode est appelée par Styler.apply(axis=None).
        Elle prend un DataFrame (data) et doit retourner un DataFrame de styles CSS
        de la même forme.
        """
        
        # 1. Vérification préliminaire
        if self.highlight_mask is None:
            # Si aucun masque n'est fourni, on retourne un DataFrame vide de styles
            return pd.DataFrame('', index=data.index, columns=data.columns)

        mask_input = self.highlight_mask
        
        # 2. Alignement de l'Index (gestion des lignes)
        # On s'assure que seules les lignes présentes dans 'data' sont considérées.
        # fill_value=False garantit que les lignes absentes du masque ne sont pas surlignées.
        try:
            # Tente de réindexer sur les colonnes si c'est un DataFrame de masque (pour flexibilité)
            aligned_mask = mask_input.reindex(index=data.index, columns=data.columns, fill_value=False)
        except TypeError:
            # Si c'est une Series, reindex() n'accepte pas 'columns'.
            # On réindexe juste l'index et gère la conversion Series -> DataFrame ci-dessous.
            aligned_mask = mask_input.reindex(index=data.index, fill_value=False)


        # 3. Conversion Series vers DataFrame (si nécessaire)
        # S'applique uniquement si l'utilisateur a créé le masque avec df['col'] == 'val'.
        if isinstance(aligned_mask, pd.Series):
            
            # Vérifie si la Series a un nom (nom de la colonne) et que cette colonne existe
            if aligned_mask.name in data.columns:
                # Créer un DataFrame de Faux de la taille de 'data'
                temp_df = pd.DataFrame(False, index=data.index, columns=data.columns)
                
                # Appliquer la Series (True/False) uniquement à la colonne correspondante
                temp_df[aligned_mask.name] = aligned_mask
                final_mask = temp_df
            else:
                # Masque Series sans nom de colonne valide, on annule le surlignage
                return pd.DataFrame('', index=data.index, columns=data.columns)
                
        elif isinstance(aligned_mask, pd.DataFrame):
                # Si c'était déjà un DataFrame après l'alignement, on le garde
                final_mask = aligned_mask
        else:
                # Type de masque inattendu
            return pd.DataFrame('', index=data.index, columns=data.columns)


        # 4. Création et application des styles
        highlight_style = f'background-color: {self.highlight_color}; color: #000000;'
        default_style = ''
        
        # Créer le DataFrame de styles par défaut (tous les styles sont vides)
        styles_df = pd.DataFrame(default_style, index=data.index, columns=data.columns)
        
        # Appliquer le style là où le masque final est Vrai.
        # C'est un masque de la taille exacte de 'data', donc cette opération est sûre.
        styles_df[final_mask] = highlight_style
        
        return styles_df    
    

    def apply(self):
        """
        Appliquer le style au DataFrame
        
        Cette méthode principale exécute toutes les étapes du stylage:
        1. Détecte les lignes dupliquées
        2. Crée un mappage de couleurs alternées pour les groupes
        3. Applique les styles CSS au DataFrame
        4. Met en évidence les valeurs manquantes
        5. Ajoute les styles d'en-têtes et de bordures
        
        Returns:
        --------
        pandas.io.formats.style.Styler
            DataFrame stylisé prêt à être affiché avec display()
        
        Styles appliqués:
        -----------------
        - Couleurs alternées pour les groupes dupliqués
        - Mise en évidence jaune pour les valeurs '???' ou NaN
        - En-têtes avec fond bleu, texte blanc et gras
        - Bordures grises autour de toutes les cellules
        - Espacement de 5px pour chaque cellule
        - Effet de survol avec fond jaune clair (#fff2cc)
        - Texte noir par défaut
        
        Notes:
        ------
        - Si aucun doublon n'existe, le DataFrame complet est stylisé
        - Les lignes conservent leur ordre de tri défini par sort_by_column()
        - L'objet Styler retourné peut être customisé davantage si nécessaire
        
        Exemple:
        --------
        >>> styler = DataFrameStyler(df, id_column='order_id')
        >>> styled_df = styler.apply()
        >>> # Pour afficher dans Jupyter:
        >>> display(styled_df)
        >>> 
        >>> # Pour exporter en HTML:
        >>> html = styled_df.to_html()
        >>> with open('styled_dataframe.html', 'w') as f:
        ...     f.write(html)
        
        >>> # Utilisation avec la fonction helper
        >>> styled = style_duplicates(df, id_column='user_id', colors=['#FFE6E6', '#E6F3FF'])
        >>> display(styled)
        """
        # Trouver les lignes dupliquées
        duplicate_rows = self._find_duplicates()
        
        # Déterminer quel DataFrame styliser
        if not duplicate_rows.empty:
            df_to_style = duplicate_rows.copy()
        else:
            df_to_style = self.df.copy()

        # Trier seulement si aucun tri custom n'a été appliqué
        if not self.custom_sort_applied and len(df_to_style.columns) > 0:
            first_col = df_to_style.columns[0]
            # Appliquer tri numérique pour la première colonne par défaut aussi
            df_to_style = df_to_style.sort_values(
                by=first_col,
                key=lambda x: x.apply(natural_sort_key)
            )

        # Créer le mappage de couleurs pour les données finales
        self._create_color_map(df_to_style)
        
        # --- Application des styles ---
        styled_df = df_to_style.style
        
        # 1. Mise en évidence des groupes dupliqués (Priorité basse)
        styled_df = styled_df.apply(self._highlight_duplicate_groups, axis=1)
        
        # 2. Mise en évidence des valeurs manquantes (Priorité moyenne, car cela surcharge la couleur de ligne)
        styled_df = styled_df.map(self._highlight_missing_cells)
        
        # 3. Mise en évidence par masque (Priorité haute, car on veut voir la valeur spécifique)
        # Note: On utilise 'apply' ici pour appliquer le style conditionnel au niveau de la cellule
        # _highlight_by_mask retourne un DataFrame de styles, qui surcharge les styles précédents si nécessaire.
        styled_df = styled_df.apply(self._highlight_by_mask, axis=None) # axis=None applique la fonction à l'ensemble du DataFrame
        
        # ... (set_table_styles reste inchangé)
        styled_df = styled_df.set_table_styles([
                {'selector': 'thead th', 'props': [
                    ('background-color', '#4472c4'),
                    ('color', 'white'),
                    ('font-weight', 'bold'),
                    ('border', '1px solid #8eaadb')
                ]},
                {'selector': 'tbody tr:hover td', 'props': [ 
                    ('background-color', '#fff2cc !important'), 
                    ('color', '#000000 !important')
                ]},
                {'selector': 'td, th', 'props': [
                    ('border', '1px solid #8eaadb'),
                    ('padding', '5px'),
                ]}
            ]).set_properties(**{'color': '#000000'})
        
        return styled_df

# Fonction helper pour utilisation simple
def style_duplicates(df, id_column=None, colors=None, sort=None, ascending=True, numeric=True, highlight_mask=None, highlight_color='#00FF00'):
    """
    Styliser le DataFrame avec mise en évidence des lignes dupliquées et surlignage par masque.
    
    Cette fonction est la façon la plus simple d'utiliser le DataFrameStyler.
    Elle crée automatiquement une instance de DataFrameStyler, applique le tri optionnel,
    et retourne le DataFrame stylisé prêt à être affiché.
    
    Paramètres:
    -----------
    df : pandas.DataFrame
        DataFrame à styliser
    id_column : str, par défaut=None
        Nom de la colonne pour identifier les doublons
        Si None, utilise l'index
    colors : list of str, optionnel
        Liste de codes couleur hexadécimaux pour les groupes alternés
        Par défaut: ['#E1F5FE', '#FFFFFF'] (bleu clair et blanc)
    sort : str, optionnel
        Nom de la colonne pour trier le DataFrame avant stylage
        Par défaut: None (pas de tri supplémentaire)
    ascending : bool, par défaut=True
        Ordre de tri (True: croissant, False: décroissant)
        Ne s'applique que si 'sort' est spécifié
    numeric : bool, par défaut=False
        Si True, trie les valeurs numériquement même si elles sont des strings
        Exemple: ['C1', 'C2', 'C10'] au lieu de ['C1', 'C10', 'C2']
        Ne s'applique que si 'sort' est spécifié

    highlight_mask : pandas.DataFrame ou Series (booléen), optionnel
        Masque booléen pour surligner des cellules spécifiques (ex: df['col'] == 171)
    highlight_color : str, optionnel
        Couleur de fond pour le surlignage du masque (Défaut: '#FFCCCC')
    
    Returns:
    --------
    pandas.io.formats.style.Styler
        DataFrame stylisé prêt à être affiché avec display()
    
    Exemples:
    ---------
    >>> # Exemple 1: Utilisation de base
    >>> from utils.dataframe_styler import style_duplicates
    >>> styled_df = style_duplicates(df)
    >>> display(styled_df)
    
    >>> # Exemple 2: Avec colonne ID personnalisée
    >>> style_duplicates(df, id_column='order_id')
    
    >>> # Exemple 3: Avec couleurs personnalisées
    >>> style_duplicates(df, colors=['#FFE6E6', '#E6F3FF'])
    
    >>> # Exemple 4: Application sur un échantillon
    >>> style_duplicates(df.head(50), id_column='client_id')
    
    >>> # Exemple 5: Personnalisation complète
    >>> styled_result = style_duplicates(
    >>>     df, 
    >>>     id_column='user_id', 
    >>>     colors=['#FFE6E6', '#E6F3FF', '#E6FFE6']
    >>> )
    >>> display(styled_result)
    
    >>> # Exemple 6: Export en HTML
    >>> html_output = style_duplicates(df, id_column='order_id').to_html()
    
    >>> # Exemple 7: Utilisation avec monkey patch (méthode DataFrame)
    >>> df.style_duplicates()
    >>> df.style_duplicates(id_column='product_id')
    >>> df.style_duplicates(colors=['#FFF0F0', '#F0FFF0'])
    
    >>> # Exemple 8: Avec tri par colonne
    >>> date_diff_negatif.style_duplicates(sort='diff_days')
    >>> df.style_duplicates(id_column='order_id', sort='date')
    >>> df.style_duplicates(sort='amount', ascending=False)
    
    >>> # Exemple 9: Tri numérique (C1, C2, C10 au lieu de C1, C10, C2)
    >>> df.style_duplicates(sort='Client', numeric=True)
    >>> df.style_duplicates(id_column='order_id', sort='Formule', numeric=True)
    
    >>> # Exemple 10: Utilisation dans une chaîne d'opérations
    >>> result = (df
    >>>          .query('age > 18')
    >>>          .style_duplicates(id_column='email', sort='date')
    >>>          .set_caption('Duplicate Emails in Adult Users')
    >>> )
    >>> display(result)
    
    >>> # Exemple 11: Avec surlignage par masque
    >>> # Surligne toutes les cellules où 'Matricule' est 171
    >>> mask = df['Matricule'] == 171
    >>> styled_df = style_duplicates(df, highlight_mask=mask, highlight_color='#FFFF99') # Jaune clair
    >>> display(styled_df)

    >>> # Exemple 12: Avec tous les paramètres
    >>> styled_df = style_duplicates(
    >>>     df,
    >>>     id_column='transaction_id',
    >>>     colors=['#FFE6E6', '#E6F3FF', '#E6FFE6'],
    >>>     sort='Client',
    >>>     ascending=False,
    >>>     numeric=True,
            highlight_mask=mask, 
            highlight_color='#FFFF99' # Jaune clair
    >>> )
    >>> display(styled_df)

    """
    styler = DataFrameStyler(
        df, 
        id_column=id_column, 
        colors=colors,
        highlight_mask=highlight_mask,
        highlight_color=highlight_color
    )
    
    if sort is not None:
        styler.sort_by_column(sort, ascending=ascending, numeric=numeric)
    
    return styler.apply()


# Monkey patch de la classe pandas DataFrame
pd.DataFrame.style_duplicates = style_duplicates