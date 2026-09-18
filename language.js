/* TransitCare multilingual UI + chatbot language preference */
(function () {
  const translations = {
    hi: {
      "User Login":"यूज़र लॉगिन", "Authority Login":"अथॉरिटी लॉगिन", "SMART PUBLIC TRANSPORT SUPPORT":"स्मार्ट पब्लिक ट्रांसपोर्ट सपोर्ट",
      "Better transport.":"बेहतर परिवहन।", "Better response.":"बेहतर समाधान।", "Report public transport problems, track complaints and connect with customer care through one simple platform.":"पब्लिक ट्रांसपोर्ट की समस्याएँ रिपोर्ट करें, शिकायतों को ट्रैक करें और एक ही प्लेटफ़ॉर्म से कस्टमर केयर से जुड़ें।",
      "Get Started →":"शुरू करें →", "Authority Portal":"अथॉरिटी पोर्टल", "TransitCare at a glance":"TransitCare एक नज़र में", "Real-time complaint activity across the TransitCare platform.":"TransitCare प्लेटफ़ॉर्म पर शिकायतों की रियल-टाइम स्थिति।",
      "LIVE SYSTEM STATUS":"लाइव सिस्टम स्थिति", "Updated just now":"अभी अपडेट हुआ", "Total Complaints":"कुल शिकायतें", "Pending":"लंबित", "Resolved":"समाधान हो गया",
      "Everything you need to raise a concern":"समस्या दर्ज करने के लिए ज़रूरी सब कुछ", "TransitCare creates a clear connection between passengers and transport authorities.":"TransitCare यात्रियों और परिवहन अधिकारियों के बीच सीधा संपर्क बनाता है।",
      "Easy Complaints":"आसान शिकायत दर्ज करें", "Report delays, cleanliness, overcrowding, staff behaviour and other transport issues.":"देरी, सफाई, भीड़, स्टाफ व्यवहार और अन्य परिवहन समस्याएँ रिपोर्ट करें।",
      "Track Progress":"प्रगति देखें", "Keep an eye on complaint status and see how reported issues are progressing.":"शिकायत की स्थिति देखें और उसकी प्रगति पर नज़र रखें।",
      "Customer Care":"कस्टमर केयर", "Get assistance through the TransitCare Assistant when an issue needs extra support.":"जब समस्या के लिए अतिरिक्त सहायता चाहिए, TransitCare Assistant से मदद लें।",
      "How TransitCare works":"TransitCare कैसे काम करता है", "Report":"रिपोर्ट करें", "Monitor":"निगरानी", "Resolve":"समाधान", "Submit the transport details and describe what happened.":"परिवहन की जानकारी दें और क्या हुआ, उसका विवरण लिखें।", "Authorities review complaints, priorities and confirmations.":"अधिकारी शिकायतों, प्राथमिकताओं और कन्फर्मेशन की समीक्षा करते हैं।", "Issues are updated through the complaint management process.":"शिकायत प्रबंधन प्रक्रिया के अनुसार स्थिति अपडेट होती है।",
      "Public Transport Complaint Management System":"पब्लिक ट्रांसपोर्ट शिकायत प्रबंधन प्रणाली",
      "Welcome back":"वापसी पर स्वागत है", "Sign in to your TransitCare user account":"अपने TransitCare यूज़र अकाउंट में साइन इन करें", "Sign in to your TransitCare authority account":"अपने TransitCare अथॉरिटी अकाउंट में साइन इन करें",
      "Email address":"ईमेल पता", "Password":"पासवर्ड", "Enter your password":"पासवर्ड दर्ज करें", "Sign in":"साइन इन", "New to TransitCare?":"TransitCare पर नए हैं?", "Create an account":"अकाउंट बनाएँ", "← Back to home":"← होम पर वापस जाएँ",
      "Create your account":"अपना अकाउंट बनाएँ", "Join TransitCare and make public transport better":"TransitCare से जुड़ें और पब्लिक ट्रांसपोर्ट को बेहतर बनाएँ", "Full name":"पूरा नाम", "Your name":"आपका नाम", "Create a password":"पासवर्ड बनाएँ", "Create Account":"अकाउंट बनाएँ", "Already registered?":"पहले से रजिस्टर हैं?",
      "Submit Complaint":"शिकायत दर्ज करें", "Your Complaints":"आपकी शिकायतें", "Logout":"लॉगआउट", "Community Issues":"सामुदायिक समस्याएँ", "Search complaints by route, transport type, category or issue...":"रूट, परिवहन, श्रेणी या समस्या से शिकायत खोजें...", "Clear":"साफ़ करें",
      "Complaint Overview":"शिकायत सारांश", "Operations overview":"ऑपरेशंस ओवरव्यू", "Monitor complaints, priorities and customer-care escalations.":"शिकायतों, प्राथमिकताओं और कस्टमर-केयर एस्केलेशन की निगरानी करें।", "In Review":"समीक्षा में", "Open Escalations":"खुले एस्केलेशन", "In Progress":"प्रगति में", "Resolved Escalations":"समाधान किए गए एस्केलेशन", "Complaint analytics":"शिकायत विश्लेषण", "All complaints":"सभी शिकायतें", "Review and update complaint priority and status.":"शिकायत की प्राथमिकता और स्थिति देखें व अपडेट करें।", "Customer-care escalations":"कस्टमर-केयर एस्केलेशन", "Handle requests that require additional support.":"अतिरिक्त सहायता वाले अनुरोध संभालें।", "No complaints found.":"कोई शिकायत नहीं मिली।", "No customer-care escalations yet.":"अभी कोई कस्टमर-केयर एस्केलेशन नहीं है।",
      "ID":"आईडी", "User":"यूज़र", "Transport":"परिवहन", "Route":"रूट", "Category":"श्रेणी", "Image":"इमेज", "Confirm":"कन्फर्म", "Priority":"प्राथमिकता", "Status":"स्थिति", "Save":"सेव", "Low":"कम", "Moderate":"मध्यम", "High":"उच्च", "Created":"बनाया गया", "Reason":"कारण", "Message":"संदेश", "Update":"अपडेट"
    },
    mr: {
      "User Login":"यूजर लॉगिन", "Authority Login":"अथॉरिटी लॉगिन", "SMART PUBLIC TRANSPORT SUPPORT":"स्मार्ट पब्लिक ट्रान्सपोर्ट सपोर्ट",
      "Better transport.":"चांगली वाहतूक.", "Better response.":"जलद प्रतिसाद.", "Report public transport problems, track complaints and connect with customer care through one simple platform.":"सार्वजनिक वाहतुकीच्या समस्या नोंदवा, तक्रारी ट्रॅक करा आणि एका प्लॅटफॉर्मवरून कस्टमर केअरशी संपर्क साधा.",
      "Get Started →":"सुरू करा →", "Authority Portal":"अथॉरिटी पोर्टल", "TransitCare at a glance":"TransitCare ची झलक", "Real-time complaint activity across the TransitCare platform.":"TransitCare प्लॅटफॉर्मवरील तक्रारींची रिअल-टाइम माहिती.",
      "LIVE SYSTEM STATUS":"लाइव्ह सिस्टम स्थिती", "Updated just now":"आत्ताच अपडेट", "Total Complaints":"एकूण तक्रारी", "Pending":"प्रलंबित", "Resolved":"निकाली काढलेल्या",
      "Everything you need to raise a concern":"तक्रार नोंदवण्यासाठी आवश्यक सर्व काही", "TransitCare creates a clear connection between passengers and transport authorities.":"TransitCare प्रवासी आणि वाहतूक अधिकाऱ्यांना जोडते.",
      "Easy Complaints":"सोप्या तक्रारी", "Report delays, cleanliness, overcrowding, staff behaviour and other transport issues.":"उशीर, स्वच्छता, गर्दी, कर्मचाऱ्यांचे वर्तन आणि इतर वाहतूक समस्या नोंदवा.",
      "Track Progress":"प्रगती तपासा", "Keep an eye on complaint status and see how reported issues are progressing.":"तक्रारीची स्थिती आणि प्रगती तपासा.",
      "Customer Care":"कस्टमर केअर", "Get assistance through the TransitCare Assistant when an issue needs extra support.":"अधिक मदत हवी असल्यास TransitCare Assistant कडून सहाय्य घ्या.",
      "How TransitCare works":"TransitCare कसे काम करते", "Report":"नोंदवा", "Monitor":"नियंत्रण", "Resolve":"निराकरण", "Submit the transport details and describe what happened.":"वाहतुकीची माहिती द्या आणि काय झाले ते लिहा.", "Authorities review complaints, priorities and confirmations.":"अधिकारी तक्रारी, प्राधान्य आणि कन्फर्मेशन तपासतात.", "Issues are updated through the complaint management process.":"तक्रार व्यवस्थापन प्रक्रियेनुसार माहिती अपडेट होते.",
      "Public Transport Complaint Management System":"सार्वजनिक वाहतूक तक्रार व्यवस्थापन प्रणाली",
      "Welcome back":"पुन्हा स्वागत आहे", "Sign in to your TransitCare user account":"तुमच्या TransitCare यूजर अकाउंटमध्ये साइन इन करा", "Sign in to your TransitCare authority account":"तुमच्या TransitCare अथॉरिटी अकाउंटमध्ये साइन इन करा",
      "Email address":"ईमेल पत्ता", "Password":"पासवर्ड", "Enter your password":"पासवर्ड टाका", "Sign in":"साइन इन", "New to TransitCare?":"TransitCare वर नवीन आहात?", "Create an account":"अकाउंट तयार करा", "← Back to home":"← होमवर परत जा",
      "Create your account":"तुमचे अकाउंट तयार करा", "Join TransitCare and make public transport better":"TransitCare मध्ये सामील व्हा आणि सार्वजनिक वाहतूक सुधारूया", "Full name":"पूर्ण नाव", "Your name":"तुमचे नाव", "Create a password":"पासवर्ड तयार करा", "Create Account":"अकाउंट तयार करा", "Already registered?":"आधीच रजिस्टर आहात?",
      "Submit Complaint":"तक्रार नोंदवा", "Your Complaints":"तुमच्या तक्रारी", "Logout":"लॉगआउट", "Community Issues":"सामुदायिक समस्या", "Search complaints by route, transport type, category or issue...":"रूट, वाहतूक, श्रेणी किंवा समस्येनुसार तक्रार शोधा...", "Clear":"पुसा",
      "Operations overview":"ऑपरेशन्स आढावा", "Monitor complaints, priorities and customer-care escalations.":"तक्रारी, प्राधान्ये आणि कस्टमर-केअर एस्केलेशन तपासा.", "In Review":"पुनरावलोकनात", "Open Escalations":"उघडी एस्केलेशन", "In Progress":"प्रगतीत", "Resolved Escalations":"निकाली काढलेल्या एस्केलेशन", "Complaint analytics":"तक्रार विश्लेषण", "All complaints":"सर्व तक्रारी", "Review and update complaint priority and status.":"तक्रारीचे प्राधान्य आणि स्थिती तपासा व अपडेट करा.", "Customer-care escalations":"कस्टमर-केअर एस्केलेशन", "Handle requests that require additional support.":"अतिरिक्त मदतीच्या विनंत्या हाताळा.", "No complaints found.":"तक्रारी सापडल्या नाहीत.", "No customer-care escalations yet.":"अजून कस्टमर-केअर एस्केलेशन नाही.",
      "ID":"आयडी", "User":"यूजर", "Transport":"वाहतूक", "Route":"रूट", "Category":"श्रेणी", "Image":"प्रतिमा", "Confirm":"कन्फर्म", "Priority":"प्राधान्य", "Status":"स्थिती", "Save":"सेव्ह", "Low":"कमी", "Moderate":"मध्यम", "High":"उच्च", "Created":"तयार", "Reason":"कारण", "Message":"संदेश", "Update":"अपडेट"
    }
  };

  const chatbotText = {
    en: { title:"TransitCare Assistant", online:"● Online", placeholder:"Type your message...", report:"📝 Report Issue", status:"🔎 Status", care:"👨‍💼 Customer Care", greeting:"👋 Hello! I'm the <b>TransitCare Assistant</b>.<br><br>I can help with complaints, status questions and customer-care support.<br><br>How can I help you today?" },
    hi: { title:"TransitCare Assistant", online:"● ऑनलाइन", placeholder:"अपना संदेश लिखें...", report:"📝 समस्या रिपोर्ट करें", status:"🔎 स्थिति", care:"👨‍💼 कस्टमर केयर", greeting:"👋 नमस्ते! मैं <b>TransitCare Assistant</b> हूँ।<br><br>मैं शिकायत, स्थिति और कस्टमर-केयर सहायता में मदद कर सकता हूँ।<br><br>आज मैं आपकी कैसे मदद करूँ?" },
    mr: { title:"TransitCare Assistant", online:"● ऑनलाइन", placeholder:"तुमचा संदेश लिहा...", report:"📝 समस्या नोंदवा", status:"🔎 स्थिती", care:"👨‍💼 कस्टमर केअर", greeting:"👋 नमस्कार! मी <b>TransitCare Assistant</b> आहे.<br><br>मी तक्रार, स्थिती आणि कस्टमर-केअर मदतीसाठी मार्गदर्शन करू शकतो.<br><br>आज मी तुमची कशी मदत करू?" }
  };

  function getLang(){ return localStorage.getItem('transitcare_lang') || 'en'; }
  function setLang(lang){ localStorage.setItem('transitcare_lang', lang); window.location.reload(); }
  function replaceTextNodes(root, map){
    const walker=document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes=[]; let n; while(n=walker.nextNode()) nodes.push(n);
    nodes.forEach(node=>{ const raw=node.nodeValue; const trimmed=raw.trim(); if(map[trimmed]) node.nodeValue=raw.replace(trimmed,map[trimmed]); });
  }
  function applyLanguage(){
    const lang=getLang(); const map=translations[lang] || {};
    replaceTextNodes(document.body,map);
    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el=>{ const key=el.getAttribute('data-original-placeholder') || el.placeholder; if(!el.dataset.originalPlaceholder) el.dataset.originalPlaceholder=key; if(map[key]) el.placeholder=map[key]; });
    document.documentElement.lang=lang==='hi'?'hi':lang==='mr'?'mr':'en';
    let sw=document.getElementById('languageSwitcher');
    if(!sw){
      sw=document.createElement('select');
      sw.id='languageSwitcher';
      sw.className='language-switcher';
      sw.setAttribute('aria-label','Language');
      sw.innerHTML='<option value="en">English</option><option value="hi">हिंदी</option><option value="mr">मराठी</option>';
      const actions=document.querySelector('.nav-actions');
      const nav=document.querySelector('.navbar');
      if(actions){ actions.appendChild(sw); }
      else if(nav){ nav.appendChild(sw); }
      else { document.body.appendChild(sw); }
    }
    if(!sw.dataset.languageBound){
      sw.addEventListener('change',()=>setLang(sw.value));
      sw.dataset.languageBound='1';
    }
    sw.value=lang;
  }
  window.getTransitCareLanguage=getLang;
  window.getChatbotText=()=>chatbotText[getLang()]||chatbotText.en;
  window.setTransitCareLanguage=setLang;
  document.addEventListener('DOMContentLoaded',applyLanguage);
})();
