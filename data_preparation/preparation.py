def discretize(df):
    borders = {
        'geschwindigkeit': (80, 126),
        'tonlage': (205, 423),
        'schallstaerke': (25, 49)
    }
    
    def _stringify(x, lower, upper):
        if x <= lower: return "low"
        if x >= upper: return "high"
        return "normal"
    
    for col in df:
        lower_border, upper_border = borders[col]
        
        df[col] = df[col].map(lambda x: _stringify(x, lower_border, upper_border))
    
    return df
