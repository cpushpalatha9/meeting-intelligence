def _words(s): return (s or "").lower().split()

def calculate_wer(reference,hypothesis):
    r=_words(reference); h=_words(hypothesis)
    n=len(r); m=len(h)
    if n==0: return {"wer":0.0,"accuracy":1.0,"reference_words":0,"substitutions":0,"deletions":0,"insertions":m}
    d=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): d[i][0]=i
    for j in range(m+1): d[0][j]=j
    for i in range(1,n+1):
        for j in range(1,m+1):
            cost=0 if r[i-1]==h[j-1] else 1
            d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+cost)
    wer=d[n][m]/n
    return {"wer":wer,"accuracy":max(0.0,1-wer),"reference_words":n,"hypothesis_words":m,"edit_distance":d[n][m]}

