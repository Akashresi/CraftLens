export const SUPPORTED_WEB_LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिंदी" },
  { code: "ta", label: "தமிழ்" },
  { code: "te", label: "తెలుగు" },
  { code: "kn", label: "ಕನ್ನಡ" },
  { code: "ml", label: "മലയാളം" },
  { code: "bn", label: "বাংলা" },
  { code: "mr", label: "मराठी" },
];

type TranslationKeys = {
  discoverCrafts: string;
  heritageOrigins: string;
  wholesaleB2B: string;
  artisanStudio: string;
  catalogTitle: string;
  catalogSubtitle: string;
  searchPlaceholder: string;
  loadingCrafts: string;
  emptyCatalog: string;
  signIn: string;
};

const DICT: Record<string, TranslationKeys> = {
  en: {
    discoverCrafts: "Discover Crafts",
    heritageOrigins: "Heritage Origins",
    wholesaleB2B: "Wholesale & B2B",
    artisanStudio: "Artisan Studio",
    catalogTitle: "Authentic Handmade Crafts",
    catalogSubtitle: "Direct from GI-verified Indian artisan clusters with living-wage transparency.",
    searchPlaceholder: "Search sarees, pottery, wooden toys, Dhokra...",
    loadingCrafts: "Loading authentic crafts...",
    emptyCatalog: "No crafts matched your filter criteria.",
    signIn: "Sign In",
  },
  hi: {
    discoverCrafts: "शिल्प खोजें",
    heritageOrigins: "विरासत और GI",
    wholesaleB2B: "थोक व B2B",
    artisanStudio: "कारीगर स्टूडियो",
    catalogTitle: "प्रामाणिक हस्तनिर्मित शिल्प",
    catalogSubtitle: "GI-सत्यापित भारतीय कारीगर समूहों से उचित मजदूरी पारदर्शिता के साथ सीधे।",
    searchPlaceholder: "साड़ी, मिट्टी के बर्तन, लकड़ी के खिलौने खोजें...",
    loadingCrafts: "शिल्प लोड हो रहे हैं...",
    emptyCatalog: "आपके फ़िल्टर से कोई शिल्प मेल नहीं खाया।",
    signIn: "साइन इन करें",
  },
  ta: {
    discoverCrafts: "கைவினைப் பொருட்கள்",
    heritageOrigins: "பாரம்பரியம் & GI",
    wholesaleB2B: "மொத்த விற்பனை",
    artisanStudio: "கலைஞர் ஸ்டுடியோ",
    catalogTitle: "அசல் கைவினைப் பொருட்கள்",
    catalogSubtitle: "GI சான்றளிக்கப்பட்ட இந்திய கைவினைஞர்களிடமிருந்து நேரடி நியாய விலை விற்பனை.",
    searchPlaceholder: "பட்டுப் புடவை, மண்பாண்டம், மரப் பொம்மை தேடவும்...",
    loadingCrafts: "கைவினைப் பொருட்கள் ஏற்றப்படுகிறது...",
    emptyCatalog: "தேடலுக்கு பொருந்தும் கைவினைப் பொருட்கள் இல்லை.",
    signIn: "உள்நுழைக",
  },
  te: {
    discoverCrafts: "హస్తకళలు",
    heritageOrigins: "వారసత్వం & GI",
    wholesaleB2B: "హోల్‌సేల్ & B2B",
    artisanStudio: "కళాకారుల స్టూడియో",
    catalogTitle: "అసలైన చేతిపనులు",
    catalogSubtitle: "GI-ధృవీకరించబడిన భారతీయ కళాకారుల నుండి నేరుగా న్యాయమైన వేతనంతో.",
    searchPlaceholder: "పట్టు చీరలు, మట్టి పాత్రలు, కొయ్య బొమ్మలు వెతకండి...",
    loadingCrafts: "హస్తకళలు లోడ్ అవుతున్నాయి...",
    emptyCatalog: "మీ ఫిల్టర్‌కు సరిపోయే కళాఖండాలు లేవు.",
    signIn: "సైన్ ఇన్",
  },
  kn: {
    discoverCrafts: "ಕರಕುಶಲ ವಸ್ತುಗಳು",
    heritageOrigins: "ಪರಂಪರೆ & GI",
    wholesaleB2B: "ಸಗಟು ವ್ಯಾಪಾರ",
    artisanStudio: "ಕಲಾವಿದ ಸ್ಟುಡಿಯೋ",
    catalogTitle: "ಅಸಲಿ ಕೈಯಿಂದ ಮಾಡಿದ ಕರಕುಶಲ",
    catalogSubtitle: "GI-ಪ್ರಮಾಣೀಕೃತ ಭಾರತೀಯ ಕಲಾವಿದರಿಂದ ನ್ಯಾಯಯುತ ವೇತನದೊಂದಿಗೆ ನೇರವಾಗಿ.",
    searchPlaceholder: "ಸೀರೆ, ಮಣ್ಣಿನ ಮಡಿಕೆ, ಚನ್ನಪಟ್ಟಣ ಗೊಂಬೆ ಹುಡುಕಿ...",
    loadingCrafts: "ಕರಕುಶಲ ವಸ್ತುಗಳು ಲೋಡ್ ಆಗುತ್ತಿವೆ...",
    emptyCatalog: "ನಿಮ್ಮ ಹುಡುಕಾಟಕ್ಕೆ ಯಾವುದೇ ವಸ್ತು ಸಿಗಲಿಲ್ಲ.",
    signIn: "ಸೈನ್ ಇನ್",
  },
  ml: {
    discoverCrafts: "കരകൗശല വസ്തുക്കൾ",
    heritageOrigins: "പൈതൃകം & GI",
    wholesaleB2B: "മൊത്തവ്യാപാരം",
    artisanStudio: "ആർട്ടിസാൻ സ്റ്റുഡിയോ",
    catalogTitle: "തനതായ കരകൗശല ഉൽപ്പന്നങ്ങൾ",
    catalogSubtitle: "GI-സാക്ഷ്യപ്പെടുത്തിയ ഇന്ത്യൻ കരകൗശല വിദഗ്ധരിൽ നിന്ന് നേരിട്ട്.",
    searchPlaceholder: "സാരി, മൺപാത്രം, തടിക്കളിപ്പാട്ടം തിരയുക...",
    loadingCrafts: "ഉൽപ്പന്നങ്ങൾ ലോഡ് ചെയ്യുന്നു...",
    emptyCatalog: "നിങ്ങളുടെ തിരയലുമായി പൊരുത്തപ്പെടുന്നവ കണ്ടെത്തിയില്ല.",
    signIn: "സൈൻ ഇൻ",
  },
  bn: {
    discoverCrafts: "হস্তশিল্প",
    heritageOrigins: "ঐতিহ্য ও GI",
    wholesaleB2B: "পাইকারি B2B",
    artisanStudio: "কারিগর স্টুডিও",
    catalogTitle: "খাঁটি হাতে তৈরি শিল্পকর্ম",
    catalogSubtitle: "GI-যাচাইকৃত ভারতীয় কারিগরদের কাছ থেকে ন্যায্য মজুরিসহ সরাসরি।",
    searchPlaceholder: "শাড়ি, পোড়ামাটি, কাঠের পুতুল খুঁজুন...",
    loadingCrafts: "শিল্পকর্ম লোড হচ্ছে...",
    emptyCatalog: "আপনার অনুসন্ধানের সাথে মেলে এমন কোনো পণ্য নেই।",
    signIn: "সাইন ইন",
  },
  mr: {
    discoverCrafts: "हस्तकला पहा",
    heritageOrigins: "वारसा आणि GI",
    wholesaleB2B: "घाऊक B2B",
    artisanStudio: "कारागीर स्टुडिओ",
    catalogTitle: "अस्सल हस्तनिर्मित कलाकृती",
    catalogSubtitle: "GI-प्रमाणित भारतीय कारागिरांकडून योग्य मोबदल्यासह थेट खरेदी.",
    searchPlaceholder: "पैठणी साडी, मातीची भांडी, लाकडी खेळणी शोधा...",
    loadingCrafts: "कलाकृती लोड होत आहेत...",
    emptyCatalog: "तुमच्या शोधाशी जुळणारी कोणतीही कलाकृती सापडली नाही.",
    signIn: "साइन इन करा",
  },
};

export function tWeb(language: string, key: keyof TranslationKeys): string {
  const dict = DICT[language] || DICT.en;
  return dict[key] || DICT.en[key];
}

