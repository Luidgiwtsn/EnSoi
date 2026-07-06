import { jsPDF } from 'jspdf';
/**
 * Nettoie les caracteres Unicode que les polices PostScript standard
 * (helvetica, times, courier) de jsPDF ne connaissent pas.
 *
 * Sans ce nettoyage, ces caracteres apparaissent comme des '/' parasites
 * dans le PDF ou provoquent des coupures brutales de texte.
 *
 * Caracteres traites :
 * - \u202f (NARROW NO-BREAK SPACE) : espace insecable etroit, utilise
 *   par les modeles de langage francais autour de la ponctuation.
 * - \u00a0 (NO-BREAK SPACE) : espace insecable standard.
 * - \u2011 (NON-BREAKING HYPHEN) : tiret insecable.
 * - \u2028, \u2029 (LINE/PARAGRAPH SEPARATOR) : separateurs Unicode.
 *
 * @param {string} texte - Texte a nettoyer
 * @returns {string} - Texte compatible helvetica
 */
function nettoyerTexteUnicode(texte) {
  if (!texte) return '';
  return String(texte)
    .replace(/\u202f/g, ' ')  // narrow no-break space
    .replace(/\u00a0/g, ' ')  // no-break space
    .replace(/\u2011/g, '-')  // non-breaking hyphen
    .replace(/\u2028/g, '\n') // line separator
    .replace(/\u2029/g, '\n\n'); // paragraph separator
}

/**
 * Genere un PDF d'un profil EnSoi et declenche son telechargement.
 *
 * Format A4 portrait, charte EnSoi (vert sauge + dore + creme).
 * Sections :
 *   1. En-tete : titre + nom complet + date de naissance + date de generation
 *   2. Numérologie : chemin de vie, expression, intime, réalisation
 *   3. Profil Cognitif : type + 4 dimensions avec pourcentages
 *   4. Human Design : type, strategie, profil, autorite
 *   5. Synthèse IA : texte multi-lignes (ou message "non disponible" si statut=partiel)
 *
 * Le claim_token n'est jamais inclus (securite).
 * L'heure, le pays et le fuseau de naissance ne sont pas inclus (decision MVP).
 *
 * @param {object} profil - Objet ProfilComplet retourne par le backend
 */
export function generateProfilPDF(profil) {
  // Couleurs EnSoi (HEX) - cohérent avec tailwind.config.js
  const COLORS = {
    dark: '#3D4A3D',      // vert sauge fonce - titres
    primary: '#95A390',   // vert sauge - titres de section
    secondary: '#B0A37F', // dore sable - separateurs et accents
    muted: '#7A8478',     // vert-gris - texte secondaire
    body: '#1F2937',      // gris fonce - corps du texte
  };

  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const PAGE_WIDTH = 210;
  const MARGIN = 20;
  const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN;
  let y = MARGIN;

  // Helper : ajoute une ligne de separation doree
  const drawSeparator = () => {
    doc.setDrawColor(COLORS.secondary);
    doc.setLineWidth(0.5);
    doc.line(MARGIN, y, PAGE_WIDTH - MARGIN, y);
    y += 6;
  };

  // Helper : titre de section
  const sectionTitle = (text) => {
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(COLORS.primary);
    doc.text(text, MARGIN, y);
    y += 7;
  };

  // Helper : ligne label + valeur
  const labelValue = (label, value) => {
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(COLORS.muted);
    doc.text(`${label} :`, MARGIN, y);
    doc.setTextColor(COLORS.body);
    doc.text(String(value), MARGIN + 50, y);
    y += 6;
  };

  // === 1. EN-TETE ===
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(22);
  doc.setTextColor(COLORS.dark);
  doc.text('Profil EnSoi', MARGIN, y);
  y += 10;

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(13);
  doc.setTextColor(COLORS.body);
  doc.text(`${profil.prenom} ${profil.nom_famille}`, MARGIN, y);
  y += 6;

  const dateNaissance = new Date(profil.date_naissance).toLocaleDateString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  });
  const dateGeneration = new Date(profil.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  });
  doc.setFontSize(10);
  doc.setTextColor(COLORS.muted);
  doc.text(`Né(e) le ${dateNaissance}  -  Profil généré le ${dateGeneration}`, MARGIN, y);
  y += 10;

  drawSeparator();

  // === 2. NUMEROLOGIE ===
  sectionTitle('Numérologie');
  labelValue('Chemin de vie', profil.numerologie.chemin_vie);
  labelValue('Expression', profil.numerologie.expression);
  labelValue('Intime', profil.numerologie.intime);
  labelValue('Réalisation', profil.numerologie.realisation);
  y += 4;

  // === 3. PROFIL COGNITIF ===
  sectionTitle('Profil Cognitif');
  labelValue('Type', profil.profil_cognitif.nom_profil);
  const dims = profil.profil_cognitif.dimensions;
  labelValue('Énergie', `${dims.energie.dominant} (${dims.energie.score_pourcentage}%)`);
  labelValue('Perception', `${dims.perception.dominant} (${dims.perception.score_pourcentage}%)`);
  labelValue('Décision', `${dims.decision.dominant} (${dims.decision.score_pourcentage}%)`);
  labelValue('Organisation', `${dims.organisation.dominant} (${dims.organisation.score_pourcentage}%)`);
  y += 4;

  // === 4. HUMAN DESIGN ===
  sectionTitle('Human Design');
  labelValue('Type', profil.human_design.type_hd);
  labelValue('Stratégie', profil.human_design.strategie);
  labelValue('Profil', profil.human_design.profil);
  labelValue('Autorité', profil.human_design.autorite);
  if (!profil.human_design.donnees_completes) {
    doc.setFont('helvetica', 'italic');
    doc.setFontSize(9);
    doc.setTextColor(COLORS.muted);
    doc.text('(Heure de naissance non fournie — calcul partiel)', MARGIN, y);
    y += 5;
  }
  y += 4;

  drawSeparator();

  // === 5. SYNTHESE IA ===
  sectionTitle('Synthèse personnelle');
  if (profil.synthese_ia && profil.statut === 'complet') {
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(COLORS.body);

    // Nettoyage des caracteres Unicode incompatibles avec helvetica
    const syntheseNettoyee = nettoyerTexteUnicode(profil.synthese_ia);

    // Decoupage par paragraphes (le modele Groq retourne \n\n entre chaque §)
    const paragraphes = syntheseNettoyee.split(/\n\s*\n/);

    paragraphes.forEach((paragraphe, indexParagraphe) => {
      const lignes = doc.splitTextToSize(paragraphe.trim(), CONTENT_WIDTH);
      lignes.forEach((ligne) => {
        // Saut de page si on deborde
        if (y > 280) {
          doc.addPage();
          y = MARGIN;
        }
        doc.text(ligne, MARGIN, y);
        y += 5;
      });
      // Espace entre paragraphes (sauf apres le dernier)
      if (indexParagraphe < paragraphes.length - 1) {
        y += 3;
      }
    });
  } else {
    doc.setFont('helvetica', 'italic');
    doc.setFontSize(10);
    doc.setTextColor(COLORS.muted);
    doc.text(
      'Synthèse non disponible (le service IA était indisponible lors de la génération).',
      MARGIN,
      y
    );
    y += 5;
  }

  // === TELECHARGEMENT ===
  const dateFichier = new Date(profil.created_at)
    .toISOString()
    .slice(0, 10)
    .replace(/-/g, '');
  const nomFichier = `ensoi-profil-${profil.prenom}-${profil.nom_famille}-${dateFichier}.pdf`
    .toLowerCase()
    .replace(/\s+/g, '-');

  doc.save(nomFichier);
}
