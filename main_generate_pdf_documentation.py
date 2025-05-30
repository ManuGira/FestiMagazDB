import os
import subprocess
from pypdf import PdfReader, PdfWriter

DOSSIER_DOC = "./doc"
DOSSIER_TMP = "./build/tmp"
FICHIER_SORTIE = "./build/FestiMagazDB documentation.pdf"
FICHIER_PAGE_BLANCHE = os.path.join(DOSSIER_TMP, "blank.pdf")


def verifier_pandoc():
    """Vérifie que Pandoc est installé"""
    from shutil import which
    if which("pandoc") is None:
        raise EnvironmentError("Pandoc n'est pas installé ou pas dans le PATH.")


def lister_fichiers_md(dossier):
    """Retourne la liste triée des fichiers .md dans le dossier"""
    return sorted([
        f for f in os.listdir(dossier)
        if f.endswith(".md")
    ])


def convertir_md_en_pdf(fichier_md, dossier_source, dossier_cible):
    """Convertit un fichier .md en .pdf avec Pandoc, depuis le dossier doc"""
    source = os.path.join(dossier_source, fichier_md)
    nom_sans_ext = os.path.splitext(fichier_md)[0]
    cible = os.path.join(dossier_cible, f"{nom_sans_ext}.pdf")

    cmd = [
        "pandoc",
        source,
        "-o", cible,
        "--resource-path=" + dossier_source
    ]
    subprocess.run(cmd, check=True)
    return cible


def generer_page_blanche(fichier_sortie):
    """Crée un fichier PDF d'une seule page blanche (A4)"""
    writer = PdfWriter()
    writer.add_blank_page(width=595.2, height=841.8)  # Format A4
    with open(fichier_sortie, "wb") as f:
        writer.write(f)


def fusionner_pdfs_avec_blancs(fichiers_pdf, fichier_blanche, fichier_resultat):
    """Fusionne tous les PDF avec insertion de page blanche après les documents impairs"""
    final_writer = PdfWriter()
    page_blanche = PdfReader(fichier_blanche).pages[0]

    for fichier in fichiers_pdf:
        reader = PdfReader(fichier)
        for page in reader.pages:
            final_writer.add_page(page)

        if len(reader.pages) % 2 != 0:
            final_writer.add_page(page_blanche)

    with open(fichier_resultat, "wb") as f:
        final_writer.write(f)


def main():
    verifier_pandoc()

    os.makedirs(DOSSIER_TMP, exist_ok=True)
    fichiers_md = lister_fichiers_md(DOSSIER_DOC)
    fichiers_pdf = []

    print("Conversion Markdown -> PDF...")
    for fichier_md in fichiers_md:
        fichier_pdf = convertir_md_en_pdf(fichier_md, DOSSIER_DOC, DOSSIER_TMP)
        fichiers_pdf.append(fichier_pdf)
        print(f"{fichier_pdf}")

    print("Génération de page blanche...")
    generer_page_blanche(FICHIER_PAGE_BLANCHE)

    print("Fusion finale...")
    fusionner_pdfs_avec_blancs(fichiers_pdf, FICHIER_PAGE_BLANCHE, FICHIER_SORTIE)

    print(f"PDF final généré : {FICHIER_SORTIE}")


if __name__ == "__main__":
    main()
