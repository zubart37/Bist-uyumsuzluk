from datetime import date

# ==========================================
# 30 EYLÜL 2026'YA KADAR BIST 50
# ==========================================

BIST50_Q3_2026 = [
    "BTCIM.IS",
    "TCELL.IS",
    "KUYAS.IS",
    "TTKOM.IS",
    "PETKM.IS",
    "MGROS.IS",
    "SISE.IS",
    "ENKAI.IS",
    "AKSEN.IS",
    "HALKB.IS",
    "YKBNK.IS",
    "VAKBN.IS",
    "GARAN.IS",
    "AKBNK.IS",
    "TOASO.IS",
    "TUPRS.IS",
    "BIMAS.IS",
    "FROTO.IS",
    "ECILC.IS",
    "ASELS.IS",
    "KRDMD.IS",
    "CIMSA.IS",
    "BRSAN.IS",
    "KCHOL.IS",
    "CCOLA.IS",
    "AEFES.IS",
    "ULKER.IS",
    "THYAO.IS",
    "ALARK.IS",
    "HEKTS.IS",
    "SAHOL.IS",
    "TAVHL.IS",
    "PGSUS.IS",
    "SASA.IS",
    "EREGL.IS",
    "ISCTR.IS",
    "EKGYO.IS",
    "GUBRF.IS",
    "OYAKC.IS",
    "TURSG.IS",
    "CANTE.IS",
    "MIATK.IS",
    "ASTOR.IS",
    "KTLEV.IS",
    "PASEU.IS",
    "GLRMK.IS",
    "DSTKF.IS",
    "EFOR.IS",
    "TRMET.IS",
    "TRALT.IS",
]


# ==========================================
# 1 EKİM - 31 ARALIK 2026 BIST 50
# ==========================================

BIST50_Q4_2026 = [
    "BTCIM.IS",
    "TCELL.IS",
    "TTKOM.IS",
    "PETKM.IS",
    "MGROS.IS",
    "SISE.IS",
    "ENKAI.IS",
    "AKSEN.IS",
    "HALKB.IS",
    "YKBNK.IS",
    "VAKBN.IS",
    "GARAN.IS",
    "AKBNK.IS",
    "TOASO.IS",
    "TUPRS.IS",
    "BIMAS.IS",
    "FROTO.IS",
    "ECILC.IS",
    "ASELS.IS",
    "KRDMD.IS",
    "CIMSA.IS",
    "BRSAN.IS",
    "KCHOL.IS",
    "CCOLA.IS",
    "AEFES.IS",
    "ULKER.IS",
    "THYAO.IS",
    "ALARK.IS",
    "HEKTS.IS",
    "SAHOL.IS",
    "TAVHL.IS",
    "PGSUS.IS",
    "SASA.IS",
    "EREGL.IS",
    "ISCTR.IS",
    "EKGYO.IS",
    "GUBRF.IS",
    "OYAKC.IS",
    "TURSG.IS",
    "CANTE.IS",
    "ASTOR.IS",
    "GLRMK.IS",
    "TRMET.IS",
    "TRALT.IS",

    # 1 Ekim 2026'da BIST 50'ye girenler
    "CVKMD.IS",
    "CWENE.IS",
    "DOAS.IS",
    "ENERY.IS",
    "MAVI.IS",
    "TSKB.IS",
]


# ==========================================
# TARİHE GÖRE LİSTEYİ SEÇ
# ==========================================

if date.today() >= date(2026, 10, 1):
    STOCKS = BIST50_Q4_2026
else:
    STOCKS = BIST50_Q3_2026