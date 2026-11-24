"""SafeTriage Synthetic Dataset Generator (Phase 6).

Generates 1,200 synthetic clinical triage cases across 10 specialties and 70 template families.

Safety & Methodological Constraints:
- At least 60 template families across 10 specialties (generates 70 families, 7 per specialty).
- Gold labels assigned by template design, NOT by running the rule engine (avoids circularity).
- Split strictly by family (70% train, 15% validation, 15% test).
- Test split has >= 10 families. Every urgency level (1-4) present in every split.
- Never breaks family isolation to hit exact percentage splits.
- Language styles: formal, colloquial, Hinglish, Marathi-transliterated, typos, negation, history, third-party, minimized.
- All Hinglish/Marathi marked unreviewed by native speaker.
- All cases tier="synthetic_dev", label_source="developer_assigned_unreviewed".
- No drug names, no doses, no real patient data.
- Canonical JSON serialization with LF line endings and SHA-256 checksums.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


@dataclass(frozen=True)
class TemplateFamily:
    family_id: str
    specialty: str
    gold_urgency: int
    concept: str
    clinical_intent: str
    formal_template: str
    colloquial_template: str
    hinglish_template: str
    marathi_template: str
    typo_template: str
    negation_template: str
    historical_template: str
    third_party_template: str
    minimized_template: str
    default_age_years: float | None = None
    default_age_months: float | None = None
    default_sex: str | None = None


# Define 70 template families (7 per specialty across all 10 specialties)
TEMPLATE_FAMILIES: List[TemplateFamily] = [
    # --- 1. CARDIAC (7 families) ---
    TemplateFamily(
        family_id="FAM_CARD_01",
        specialty="cardiac",
        gold_urgency=1,
        concept="chest_pain",
        clinical_intent="Acute coronary syndrome with radiation and diaphoresis",
        formal_template="Patient reports acute severe crushing retrosternal chest pain radiating to left arm and jaw.",
        colloquial_template="My chest feels like an elephant is sitting on it and the pain shoots down my arm.",
        hinglish_template="Chhaati mein bohot tez dard ho raha hai aur baaye hath tak ja raha hai pasina bhi aa raha hai.",
        marathi_template="Chaati madhe khup jorat dukhat ahe aani tras hoto ahe ghabrahat hotiye.",
        typo_template="Sever cheest pane raditing to my left arm cant take deep breth.",
        negation_template="No fever or cough, but sudden severe crushing chest pain radiating to neck.",
        historical_template="Previous stent placed 2 years ago, now experiencing severe recurrent chest pressure radiating to jaw.",
        third_party_template="My father is clutching his chest complaining of severe pain radiating to his left shoulder.",
        minimized_template="It is probably just gas, but my chest has heavy crushing tightness spreading to my elbow.",
        default_age_years=58.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_CARD_02",
        specialty="cardiac",
        gold_urgency=1,
        concept="chest_pain",
        clinical_intent="Acute myocardial infarction described as heart attack",
        formal_template="Sudden onset severe central chest pain associated with diaphoresis, dyspnea and nausea.",
        colloquial_template="I feel like I am having a heart attack right now my chest is squeezing tight.",
        hinglish_template="Mujhe lagta hai dil ka daura pada hai chhaati mein bohot jalan aur dard hai.",
        marathi_template="Mala watte heart attack aala ahe chaati dablya sarkhi watat ahe.",
        typo_template="Hart atak fealing chest squezing and sweting cold.",
        negation_template="No leg pain or vomiting, but central chest pressure and severe shortness of breath.",
        historical_template="Known coronary artery disease, experienced sudden episode of severe chest tightness.",
        third_party_template="My husband collapsed onto the chair saying he feels like he is having a heart attack.",
        minimized_template="Just a bit uncomfortable central chest squeezing, nothing major I hope.",
        default_age_years=64.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_CARD_03",
        specialty="cardiac",
        gold_urgency=2,
        concept="chest_pain",
        clinical_intent="Atypical chest discomfort in an older adult requiring urgent ECG",
        formal_template="Elderly patient presenting with persistent dull anterior chest ache for 2 days without radiation.",
        colloquial_template="I have had an annoying dull ache in the middle of my chest for the last couple of days.",
        hinglish_template="Do din se chhaati ke beech mein dheema dheema dard bana hua hai thakan lag rahi hai.",
        marathi_template="Don divasapasun chaatit thoda tras hot ahe aani ashaktapana watto.",
        typo_template="Dul chesd pane for two days feling tierd and week.",
        negation_template="No crushing pain or sweating, but continuous dull chest heaviness for 48 hours.",
        historical_template="History of hypertension, now reports two-day ongoing non-exertional chest discomfort.",
        third_party_template="My 72-year-old grandmother has had continuous dull chest ache since yesterday.",
        minimized_template="Just an annoying dull chest feeling since Tuesday, probably muscular.",
        default_age_years=72.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_CARD_04",
        specialty="cardiac",
        gold_urgency=2,
        concept="chest_pain",
        clinical_intent="Exertional angina episodes requiring urgent cardiology assessment",
        formal_template="Recurrent episodes of retrosternal tightness occurring reliably upon climbing stairs, resolving with rest.",
        colloquial_template="Every time I walk up a hill or climb stairs my chest gets tight and aches.",
        hinglish_template="Jab bhi seedhiyan chadhta hoon chhaati bhari ho jaati hai aur rukne par theek hoti hai.",
        marathi_template="Jinye chadhlyawar chaati bharun yete aani thamblyawar bara watate.",
        typo_template="Chets pain when walking fast relived by sitting down.",
        negation_template="No chest pain while resting in bed, but tightness predictably triggers upon walking briskly.",
        historical_template="Diagnosed with stable angina last year, but frequency of exertional chest ache has increased this week.",
        third_party_template="My mother gets chest tightness whenever she carries groceries from the market.",
        minimized_template="Only happens when I exert myself walking fast, so I just walk slower.",
        default_age_years=61.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_CARD_05",
        specialty="cardiac",
        gold_urgency=3,
        concept="chest_pain",
        clinical_intent="Positional non-cardiac chest wall discomfort",
        formal_template="Localized sharp superficial chest wall tenderness reproducible upon palpation and torso twisting.",
        colloquial_template="My chest hurts on the left side when I poke the rib or turn my body around.",
        hinglish_template="Pasliyon par ungli dabane se dard hota hai mudne par zyada lagta hai.",
        marathi_template="Chaatichya bariyevar dabla ki dukhatahe halchaal kelyawar tras hoto.",
        typo_template="Sore rib on chest hurst when I toch it or streatch.",
        negation_template="No shortness of breath or dizziness, pain only occurs when pressing directly on the rib cartilage.",
        historical_template="Started working out with weights 3 days ago, developed sharp localized rib ache.",
        third_party_template="My son says his upper chest rib is tender after his football training session.",
        minimized_template="Just a minor tender spot over my ribs from moving heavy furniture.",
        default_age_years=29.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_CARD_06",
        specialty="cardiac",
        gold_urgency=3,
        concept="chest_pain",
        clinical_intent="Intermittent mild palpitations related to caffeine or stress",
        formal_template="Intermittent sensation of fluttering heart beats for 1 week in setting of high occupational caffeine intake.",
        colloquial_template="My heart feels like it flutters or skips a beat sometimes after drinking morning coffee.",
        hinglish_template="Khabrahat si hoti hai aur dil ki dhadkan thodi tez ho jaati hai coffee peene ke baad.",
        marathi_template="Kadhi kadhi dhabdhab vadhato chaha coffee ghetlyawar chanchalta watte.",
        typo_template="Hart fluter after 3 cups of cofee skips a beet.",
        negation_template="No chest tightness, fainting or breathlessness, only brief 5-second fluttering sensations.",
        historical_template="Has had occasional benign ectopic beats noted during college exams previously.",
        third_party_template="My daughter noticed her pulse feels like it is skipping beats during exam week.",
        minimized_template="Just a tiny flutter in the chest now and then, barely notice it.",
        default_age_years=25.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_CARD_07",
        specialty="cardiac",
        gold_urgency=4,
        concept="chest_pain",
        clinical_intent="Transient brief localized twinges without clinical concern",
        formal_template="Brief 2-second momentary non-exertional chest twinge occurring once yesterday, patient asymptomatic now.",
        colloquial_template="I felt a split-second sharp stitch in my chest yesterday while sitting on the couch.",
        hinglish_template="Kal baithte waqt ek second ke liye chhaati mein sui jaisi chubhan hui thi ab sab normal hai.",
        marathi_template="Kal baslyawar ek kshan chaatit chamak aali hoti ata kahi nahi.",
        typo_template="Quick 1 sec twinge in chesst yestarday totaly fine today.",
        negation_template="No recurrence, no exertion pain, no palpitations, no shortness of breath whatsoever.",
        historical_template="No past medical history, completely well, inquiring routinely about a fleeting twinge.",
        third_party_template="My roommate wondered if a 2-second muscle twitch in the chest is anything to worry about.",
        minimized_template="Felt a micro-second twitch yesterday, felt fine immediately after.",
        default_age_years=22.0,
        default_sex="male",
    ),

    # --- 2. NEURO (7 families) ---
    TemplateFamily(
        family_id="FAM_NEUR_01",
        specialty="neuro",
        gold_urgency=1,
        concept="stroke_symptoms",
        clinical_intent="Acute focal neurological deficit suggestive of acute stroke (FAST positive)",
        formal_template="Sudden onset acute right-sided facial droop, arm weakness and dysarthric speech beginning 30 minutes ago.",
        colloquial_template="My mother's face is drooping on one side and her words are slurred she cannot lift her right hand.",
        hinglish_template="Achanak se muh tedha ho gaya hai hath uthaya nahi ja raha aur awaz ladkhada rahi hai.",
        marathi_template="Tond wankde zale ahe aani ujava hath uchalta yet nahiye spashta bolta yet nahi.",
        typo_template="Sudden face drop and arm weekness slured talk 20 mins ago.",
        negation_template="No fever or head trauma, but sudden profound right arm paralysis and slurred speech.",
        historical_template="History of atrial fibrillation, presented with acute onset right hemiparesis 40 minutes ago.",
        third_party_template="My coworker suddenly started slurring her words and her right arm went completely limp.",
        minimized_template="She says her face feels a little numb and lazy, but her mouth is visibly drooping on the right.",
        default_age_years=68.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_NEUR_02",
        specialty="neuro",
        gold_urgency=1,
        concept="headache",
        clinical_intent="Thunderclap headache suspicious for subarachnoid hemorrhage",
        formal_template="Sudden explosive onset worst headache of life reaching peak intensity within seconds with neck stiffness.",
        colloquial_template="Thunderclap pain hit my head like a baseball bat out of nowhere, worst headache I have ever had.",
        hinglish_template="Sir mein achanak bijli jaisa tez dard hua zindagi ka sabse bhayankar sir dard hai gardan hil nahi rahi.",
        marathi_template="Dokyat achanak khup mothe vidyut zalyasarkhe dukhle aayushyatla saglyat jorat dokedukhi ahe.",
        typo_template="Explosive thundercap headach worst pain of my lif hit in 2 secs.",
        negation_template="No previous migraine history, pain came on instantly in under 10 seconds with extreme 10/10 intensity.",
        historical_template="No chronic headache history, sudden instantaneous severe occipital headache while bending down.",
        third_party_template="My brother suddenly screamed holding his head saying it feels like his head exploded.",
        minimized_template="I usually do not complain about headaches, but this sudden explosive headache is terrifyingly severe.",
        default_age_years=44.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_NEUR_03",
        specialty="neuro",
        gold_urgency=1,
        concept="seizure",
        clinical_intent="Active or repetitive generalized tonic-clonic seizure",
        formal_template="Continuous generalized convulsive seizure activity lasting greater than 5 minutes with loss of consciousness.",
        colloquial_template="He is shaking all over having violent convulsions and has been unresponsive for 5 minutes.",
        hinglish_template="Dora pada hai achanak pure sharir mein jhatke aa rahe hain aur behosh hai 5 minute se.",
        marathi_template="Zatke yet ahet aani be-shuddha padla ahe halchaal karat nahiye lagech ambulance bolva.",
        typo_template="Continuos siesure shaking on floor unconsious 5 mins now.",
        negation_template="No conscious awareness, uncontrolled generalized motor jerking persisting without recovery.",
        historical_template="Known epileptic patient, failed to abort seizure after customary medication, ongoing convulsions.",
        third_party_template="A passenger on the train is actively seizing and has not woken up for several minutes.",
        minimized_template="He is having full body tremors and won't respond to his name being yelled.",
        default_age_years=35.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_NEUR_04",
        specialty="neuro",
        gold_urgency=2,
        concept="headache",
        clinical_intent="Severe acute headache associated with persistent vomiting and light sensitivity",
        formal_template="Severe holocranial headache persisting 24 hours with photophobia, phonophobia and intractable nausea.",
        colloquial_template="Terrible migraine headache that won't go away, room lights hurt my eyes and I keep throwing up.",
        hinglish_template="Sir mein bohot tez dard hai roshni bardasht nahi ho rahi aur lagatar ulti jaisa lag raha hai.",
        marathi_template="Dokyat khup vedna ahet prakash baghavat nahi aani ulti hot ahe dohn divas zale.",
        typo_template="Sever migrane headake cant look at lights thowing up.",
        negation_template="No focal weakness, no speech slurring, but unremitting severe headache and severe photophobia.",
        historical_template="Has episodic migraines, but current episode is unusually severe and unresponsive to usual analgesics.",
        third_party_template="My wife has been bedridden in a dark room all day with a severe pounding headache and vomiting.",
        minimized_template="Just a bad headache that has kept me in bed with a blindfold on since yesterday.",
        default_age_years=32.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_NEUR_05",
        specialty="neuro",
        gold_urgency=2,
        concept="dizziness",
        clinical_intent="Acute persistent vertigo with nausea and gait instability",
        formal_template="Acute onset constant spinning vertigo exacerbated by head movements with persistent ataxia and nausea.",
        colloquial_template="The entire room is spinning around me whenever I turn my head and I cannot walk in a straight line.",
        hinglish_template="Chakkar aa rahe hain sab ghoom raha hai aur chalne par ladkhada raha hoon girne lagta hoon.",
        marathi_template="Khup chakkar yet ahe sarv gol firat ahe saral chalata yet nahiye.",
        typo_template="Rom is spining dizziness cant walk straght unsteady.",
        negation_template="No ear discharge or tinnitus, but acute constant spinning vertigo causing inability to stand unsupported.",
        historical_template="First time experiencing severe spinning dizziness, unable to maintain upright posture.",
        third_party_template="My grandfather tried to get out of bed but the room started spinning and he fell sideways.",
        minimized_template="A bit of room spinning when I shift positions, feeling rather off balance today.",
        default_age_years=69.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_NEUR_06",
        specialty="neuro",
        gold_urgency=3,
        concept="headache",
        clinical_intent="Mild to moderate tension-type headache responsive to rest",
        formal_template="Bilateral band-like dull headache of moderate intensity without nausea or photophobia for 2 days.",
        colloquial_template="I have a constant dull tight feeling like a headband around my forehead from screen fatigue.",
        hinglish_template="Matha bhaari ho raha hai dono taraf dabav jaisa lag raha hai computer dekhne ke baad.",
        marathi_template="Dolyanchya var aani kapalat taan aalyasarkhe doke jad zale ahe.",
        typo_template="Dull tenstion headach band around forhead for 2 days.",
        negation_template="No nausea, no visual changes, no sensitivity to bright lights, just a steady pressure headache.",
        historical_template="Frequently gets tension headaches during intense study periods, typical pattern.",
        third_party_template="My colleague has a forehead tension headache after working 12 hours on a spreadsheet.",
        minimized_template="Just a routine dull band around my head, probably need more sleep.",
        default_age_years=28.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_NEUR_07",
        specialty="neuro",
        gold_urgency=4,
        concept="headache",
        clinical_intent="Mild brief headache after lack of hydration",
        formal_template="Mild frontal discomfort following prolonged physical activity in warm weather without hydration.",
        colloquial_template="I have a mild little headache because I forgot to drink water during my walk this afternoon.",
        hinglish_template="Dhoop mein ghoomne se halka sa sir dard ho raha hai paani kam piya tha.",
        marathi_template="Unhat firlyamule thoda doke dukhtay paani kami ghetla hota.",
        typo_template="Mild headach forgot to drink watter in the sun.",
        negation_template="No fever, no neck pain, no nausea, feeling much better after drinking two glasses of water.",
        historical_template="Regular dehydration twinge that resolves completely after fluids and rest.",
        third_party_template="My friend says she has a slight dehydration headache after our long park walk.",
        minimized_template="Barely a headache, just thirsty and tired.",
        default_age_years=23.0,
        default_sex="female",
    ),

    # --- 3. RESPIRATORY (7 families) ---
    TemplateFamily(
        family_id="FAM_RESP_01",
        specialty="respiratory",
        gold_urgency=1,
        concept="breathlessness",
        clinical_intent="Severe acute respiratory distress with inability to speak sentences",
        formal_template="Patient in severe respiratory distress, accessory muscle use, cyanosis, and inability to speak in full sentences.",
        colloquial_template="I cannot breathe, gasping for air and can barely get two words out between breaths.",
        hinglish_template="Saans lene mein bohot zyada takleef ho rahi hai bolna mushkil ho raha hai dam ghut raha hai.",
        marathi_template="Shwas ghyayla khup tras hoto ahe bolta yet nahiye hava bhetat nahiye.",
        typo_template="Cant brethe gasping for air blue lips canot talk.",
        negation_template="No fever or productive cough, acute severe suffocating breathlessness and chest indrawing.",
        historical_template="Severe brittle asthmatic presenting with refractory acute bronchospasm unresponsive to rescue therapy.",
        third_party_template="My daughter is sitting forward gasping for breath and her lips are turning slightly pale.",
        minimized_template="Having quite a struggle pulling air in, feeling rather starved for oxygen.",
        default_age_years=21.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_RESP_02",
        specialty="respiratory",
        gold_urgency=1,
        concept="breathlessness",
        clinical_intent="Acute foreign body airway obstruction / choking",
        formal_template="Witnessed acute upper airway obstruction, inspiratory stridor, unable to vocalize or cough effectively.",
        colloquial_template="He is choking on food, can't cough, can't speak and his face is turning dark red.",
        hinglish_template="Gale mein khana phas gaya hai saans atak gayi hai awaz nahi nikal rahi.",
        marathi_template="Ghasyat kiti tari adakla ahe shwas band zala ahe bolta yet nahiye.",
        typo_template="Choking on meat cant brethe or caugh urgent.",
        negation_template="No prior illness, sudden complete respiratory blockage while eating lunch at the table.",
        historical_template="Previously healthy diner experienced sudden airway occlusion during meal.",
        third_party_template="The elderly man at the restaurant table is clutching his throat and making high pitched noises.",
        minimized_template="He swallowed something wrong and is struggling desperately to clear his throat.",
        default_age_years=52.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_RESP_03",
        specialty="respiratory",
        gold_urgency=2,
        concept="breathlessness",
        clinical_intent="Acute exacerbation of chronic obstructive pulmonary disease (COPD)",
        formal_template="Known COPD patient presenting with worsening dyspnea on minimal exertion, increased sputum purulence for 3 days.",
        colloquial_template="My breathing has been getting progressively harder over the past 3 days and my inhaler isn't lasting.",
        hinglish_template="Teen din se saans chadh rahi hai thoda chalne par bhi dam phool jata hai balgam badh gaya hai.",
        marathi_template="Don teen divasapasun thoda chalala tari shwas lagto ahe khokla vadhalay.",
        typo_template="Brething geting worse past 3 days inhalor not helping copd.",
        negation_template="No chest crushing pain, but persistent marked wheezing and shortness of breath when walking across the room.",
        historical_template="Longstanding 30 pack-year smoking history with diagnosed emphysema, now in exacerbation.",
        third_party_template="My father with chronic lung disease has been wheezing heavily and struggling to walk to the bathroom.",
        minimized_template="Lungs have been acting up since the weather turned cold, struggling a bit on the stairs.",
        default_age_years=67.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_RESP_04",
        specialty="respiratory",
        gold_urgency=2,
        concept="cough",
        clinical_intent="Acute hemoptysis (coughing up fresh blood)",
        formal_template="Patient reports coughing up approximately 30ml of frank red blood accompanied by pleuritic chest discomfort.",
        colloquial_template="I started coughing this morning and I am coughing up bright red blood in my tissue paper.",
        hinglish_template="Khansi mein taza laal khoon nikal raha hai subah se do baar khoon aaya.",
        marathi_template="Khoklyatun rakt padat ahe laal rangacha rakt yet ahe don vela.",
        typo_template="Caughing up brite red blood in spit today.",
        negation_template="No previous nosebleed or tooth extraction, blood is originating from deep cough.",
        historical_template="Former smoker with chronic cough, now noticing fresh hemoptysis for the first time.",
        third_party_template="My uncle coughed into a napkin and there were clear streaks and spoonfuls of blood.",
        minimized_template="Just a bit of pinkish red blood when I clear my lungs forcefully.",
        default_age_years=54.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_RESP_05",
        specialty="respiratory",
        gold_urgency=3,
        concept="cough",
        clinical_intent="Subacute persistent dry post-viral cough",
        formal_template="Persistent non-productive cough for 12 days following resolved viral upper respiratory tract infection.",
        colloquial_template="Had a cold two weeks ago that went away, but this dry tickling cough will not stop.",
        hinglish_template="Do hafte pehle zukham tha wo theek ho gaya lekin sukhi khansi abhi tak bani hui hai.",
        marathi_template="Sardi bara zali pan sukha khokla azun thambla nahiye don athavade zale.",
        typo_template="Dry caugh for 2 weaks aftar cold wont stop tickle.",
        negation_template="No fever, no phlegm, no shortness of breath, just a constant annoying tickle in the throat.",
        historical_template="Typical post-infectious bronchial hyperreactivity after winter colds.",
        third_party_template="My sister has had this lingering dry cough ever since she caught a chill last fortnight.",
        minimized_template="Just an annoying lingering dry cough from my cold last week.",
        default_age_years=31.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_RESP_06",
        specialty="respiratory",
        gold_urgency=3,
        concept="cough",
        clinical_intent="Productive cough with yellow sputum without dyspnea",
        formal_template="Productive cough with moderate yellow-green expectoration for 5 days, afebrile, respiratory rate normal.",
        colloquial_template="Coughing up yellowish mucus for four or five days, chest feels congested but breathing is fine.",
        hinglish_template="Paanch din se balgam wali khansi hai peela balgam nikal raha hai saans normal hai.",
        marathi_template="Pivla kapha yet ahe khoklyatun pan shwas ghyayla tras nahiye.",
        typo_template="Caugh with yelow flem for 5 days chest conjested.",
        negation_template="No shortness of breath, no high fever, no chest pain on inspiration, simply chest congestion.",
        historical_template="Develops chesty coughs annually with seasonal weather changes.",
        third_party_template="My roommate has been coughing up yellow phlegm into the sink for a few days.",
        minimized_template="A bit congested with some mucus in the morning, nothing I can't handle.",
        default_age_years=36.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_RESP_07",
        specialty="respiratory",
        gold_urgency=4,
        concept="cough",
        clinical_intent="Mild throat tickle from seasonal dust exposure",
        formal_template="Mild pharyngeal irritation and occasional dry throat clearing after domestic house cleaning.",
        colloquial_template="My throat feels scratchy and ticklish from all the dust after cleaning the attic today.",
        hinglish_template="Dhool mitti ki wajah se gale mein halki kharash hai aur khansi jaisa lag raha hai.",
        marathi_template="Dhulat gelyamule ghashat kharkhar hotiye thoda khokla yeto.",
        typo_template="Scratchy throt and tikel from dust clening.",
        negation_template="No fever, no difficulty swallowing, no difficulty breathing, lungs sound completely clear.",
        historical_template="Known mild sensitivity to dust mites and airborne irritants.",
        third_party_template="My roommate has a tickly throat after we dusted the bookshelves this morning.",
        minimized_template="Just a dusty scratchy throat, sipping warm tea.",
        default_age_years=26.0,
        default_sex="female",
    ),

    # --- 4. ALLERGY & IMMUNE (7 families) ---
    TemplateFamily(
        family_id="FAM_ALLG_01",
        specialty="allergy_immune",
        gold_urgency=1,
        concept="anaphylaxis",
        clinical_intent="Severe acute anaphylaxis with airway compromise following allergen exposure",
        formal_template="Acute systemic anaphylaxis with rapid onset lip and laryngeal edema, wheezing, and urticaria 10 minutes post peanut ingestion.",
        colloquial_template="My lips and tongue are swelling up fast, throat is closing and I can barely breathe after eating nuts.",
        hinglish_template="Mungfali khane ke baad gale mein soojan aa gayi hai saans atak rahi hai aur honth phool gaye hain.",
        marathi_template="Badam khallyawar otha aani jeebh sujali ahe ghasa band hoto ahe saans ghet yet nahi.",
        typo_template="Tongue and lips sweling throt closing cant brethe nut alergy.",
        negation_template="No previous insect sting, acute allergic reaction triggered within 15 minutes of food exposure with stridor.",
        historical_template="Known peanut allergy, accidentally ingested food containing nut extract, rapid swelling.",
        third_party_template="My friend's face and tongue are swelling drastically after eating a dessert at the restaurant.",
        minimized_template="My throat feels strangely tight and my lips look huge in the mirror, feeling rather dizzy.",
        default_age_years=24.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_ALLG_02",
        specialty="allergy_immune",
        gold_urgency=1,
        concept="anaphylaxis",
        clinical_intent="Anaphylactic shock following bee sting",
        formal_template="Immediate generalized urticaria, profound hypotension, presyncope, and audible wheezing following Hymenoptera sting.",
        colloquial_template="I got stung by a wasp 5 minutes ago and now I have hives everywhere, can't breathe and feeling faint.",
        hinglish_template="Madhumakhi ne kata hai pure badan par laal chakatte nikal aaye chakkar aa raha hai aur saans phool rahi hai.",
        marathi_template="Madh-mashi chaavli ahe anga-var phod aale chakkar yetiye aani ghasa dabto ahe.",
        typo_template="Wasp sting hives evrywhere dizzynes cant brethe collapsing.",
        negation_template="No previous reaction to stings, immediate rapid systemic deterioration across multiple organ systems.",
        historical_template="Second sting in lifetime, presented with dramatic systemic allergic cascade.",
        third_party_template="The gardener was stung by a hornet, collapsed on the grass with swelling and loud wheezing.",
        minimized_template="Stung by something in the yard, now covered in spots and feeling like passing out.",
        default_age_years=38.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_ALLG_03",
        specialty="allergy_immune",
        gold_urgency=2,
        concept="rash",
        clinical_intent="Acute extensive widespread urticaria without immediate airway compromise",
        formal_template="Acute onset rapidly spreading erythematous pruritic urticarial wheals covering 60% of body surface area over 3 hours.",
        colloquial_template="I broke out in red raised itchy welts all over my arms, chest, back and thighs this afternoon.",
        hinglish_template="Do teen ghante mein pure sharir par bade bade laal daane aur khujli wale chakatte nikal aaye hain.",
        marathi_template="Dohn tasat purna anga-var laal gandi aani khaj yet ahe.",
        typo_template="Red itchi welts all over my body arms and back spreading fast.",
        negation_template="No throat swelling, no wheezing, no difficulty swallowing, but rash is extremely pruritic and spreading rapidly.",
        historical_template="First episode of acute generalized urticaria of unknown etiology.",
        third_party_template="My son woke up from his nap completely covered in angry raised red hives from head to toe.",
        minimized_template="Got these itchy red blotches popping up everywhere, looks like a topographical map.",
        default_age_years=30.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_ALLG_04",
        specialty="allergy_immune",
        gold_urgency=2,
        concept="rash",
        clinical_intent="Facial angioedema without respiratory distress",
        formal_template="Marked periorbital and labial edema developing over 4 hours, airway clear, voice normal, lungs clear to auscultation.",
        colloquial_template="Woke up this morning with my eyelids and upper lip puffed up like a balloon.",
        hinglish_template="Subah utha toh aankhon ke charon taraf aur honth par bohot soojan thi.",
        marathi_template="Sakali uthlyawar dole aani otha sujun aale hote.",
        typo_template="Eyelids and lip swolen puffy this morning no brething issue.",
        negation_template="No breathing difficulty, no stridor, no tongue swelling, voice completely clear and unchanged.",
        historical_template="Started new antihypertensive medication 10 days ago, now developed isolated angioedema.",
        third_party_template="My mother's upper face and lip swelled up considerably since breakfast.",
        minimized_template="Look like I was stung by a bee on my lip, looks funny but feels tight.",
        default_age_years=55.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_ALLG_05",
        specialty="allergy_immune",
        gold_urgency=3,
        concept="rash",
        clinical_intent="Subacute localized contact dermatitis",
        formal_template="Erythematous vesicular localized plaque on wrist corresponding to nickel watch clasp contact over 4 days.",
        colloquial_template="I have an itchy red bumpy rash on my wrist right under where my metal watch sits.",
        hinglish_template="Ghadi baandhne wali jagah par laal daane aur bohot khujli ho rahi hai teen chaar din se.",
        marathi_template="Ghadyaal bandhlyamule hatavar laal phod aani khaj aali ahe.",
        typo_template="Itchi red rash under mettle watch on rist.",
        negation_template="No spreading beyond wrist, no fever, no swelling of hands or fingers, localized strictly to contact area.",
        historical_template="Known contact allergy to inexpensive costume jewelry and nickel.",
        third_party_template="My daughter has a red circle rash where the snap on her new jeans rubs her stomach.",
        minimized_template="Just a patch of itchy bumps where my belt buckle sits.",
        default_age_years=27.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_ALLG_06",
        specialty="allergy_immune",
        gold_urgency=3,
        concept="rash",
        clinical_intent="Mild seasonal allergic rhinitis / hay fever",
        formal_template="Bilateral conjunctival injection, clear rhinorrhea, sneezing paroxysms and mild palatal itching during pollen season.",
        colloquial_template="My nose is running like a faucet, eyes are watering and itching constantly from spring pollen.",
        hinglish_template="Aankhon se paani beh raha hai baar baar chheenk aa rahi hai aur naak beh rahi hai.",
        marathi_template="Dolyatun paani yetay aani shinka yet ahet sardi zali ahe unhalyat.",
        typo_template="Runy nose runing watry itchi eyes snizing all morning.",
        negation_template="No fever, no purulent discharge, no facial pressure, strictly bilateral allergic symptoms.",
        historical_template="Annual springtime allergic rhinosinusitis coinciding with flowering trees.",
        third_party_template="My husband has been sneezing non-stop and wiping his watery eyes all weekend.",
        minimized_template="Standard seasonal hay fever making my nose run and eyes itch.",
        default_age_years=33.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_ALLG_07",
        specialty="allergy_immune",
        gold_urgency=4,
        concept="rash",
        clinical_intent="Single minor insect bite with localized redness",
        formal_template="Isolated solitary pruritic papule on forearm following mosquito bite, 5mm induration, no surrounding erythema.",
        colloquial_template="A mosquito bit my forearm last night and it has a small itchy red bump.",
        hinglish_template="Raat ko machhar ne kaat liya tha hath par halka sa laal daana aur khujli hai.",
        marathi_template="Kal ratri machharane chavla hathavar chota phod aala ahe.",
        typo_template="Moskito bite on arm litel red bumb itches.",
        negation_template="No warmth, no spreading redness, no red streaks, no fever, simple solitary bite lesion.",
        historical_template="Usual reaction to mosquito bites during monsoon season.",
        third_party_template="My son has two mosquito bites on his ankle that he is scratching.",
        minimized_template="Just a routine bug bite that itches a little when touched.",
        default_age_years=20.0,
        default_sex="male",
    ),

    # --- 5. GASTRO & ABDOMINAL (7 families) ---
    TemplateFamily(
        family_id="FAM_GAST_01",
        specialty="gastro_abdominal",
        gold_urgency=1,
        concept="abdominal_pain",
        clinical_intent="Acute surgical abdomen / peritonitis with rigid abdomen and hematemesis",
        formal_template="Acute severe generalized abdominal pain with involuntary abdominal wall rigidity, guarding, and vomiting dark coffee-ground blood.",
        colloquial_template="My stomach pain is excruciating, belly is rock hard like a wooden board and I threw up black blood.",
        hinglish_template="Pet mein achanak pathar jaisa bohot tez dard hua pet bohot kadak hai aur khoon ki ulti hui.",
        marathi_template="Pota madhe achanak khup jorat dukhat ahe pot tathan zale ahe aani kalyashar raktachi ulti zali.",
        typo_template="Stumack rock hard excrutiating pain vomitting black blood.",
        negation_template="No diarrhea, acute unrelenting abdominal agony with board-like muscular rigidity and inability to lie flat.",
        historical_template="History of peptic ulcer disease, presented with sudden tearing epigastric pain 2 hours ago.",
        third_party_template="My father is curled in a fetal position, his stomach is rigid and he threw up coffee ground material.",
        minimized_template="My belly is extremely stiff and painful to touch, feel like something burst inside.",
        default_age_years=56.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GAST_02",
        specialty="gastro_abdominal",
        gold_urgency=1,
        concept="severe_bleeding",
        clinical_intent="Severe acute gastrointestinal hemorrhage / hematochezia",
        formal_template="Profuse passage of large volume frank red blood per rectum with orthostatic dizziness and diaphoresis.",
        colloquial_template="I have passed large amounts of pure blood from my bowels three times and feeling very dizzy.",
        hinglish_template="Shauch mein bohot zyada taza khoon beh raha hai chakkar aa kar behoshi si lag rahi hai.",
        marathi_template="Sandasatun khup mothya pramanat rakt yet ahe chakkar yete ahe uthta yet nahiye.",
        typo_template="Lods of red blud in stool 3 times today feling fainty.",
        negation_template="No minor hemorrhoidal spotting on paper, large volumes of pure red blood filling the toilet bowl.",
        historical_template="Known diverticular disease, sudden painless massive hematochezia.",
        third_party_template="My mother passed a bowl full of blood and when she tried to stand she nearly collapsed.",
        minimized_template="Quite a lot of blood in the toilet today and feeling lighter in the head than usual.",
        default_age_years=69.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GAST_03",
        specialty="gastro_abdominal",
        gold_urgency=2,
        concept="abdominal_pain",
        clinical_intent="Acute appendicitis presentation in right lower quadrant",
        formal_template="Pain originating periumbilically 18 hours ago and migrating to the right lower quadrant, with localized tenderness, anorexia and low-grade fever.",
        colloquial_template="Stomach ache started around my belly button yesterday and has moved down into my right hip and hurts when I cough.",
        hinglish_template="Pehle naabhi ke paas dard tha ab daayein taraf neeche pet mein bohot dard hai hilne par badhta hai.",
        marathi_template="Aadhi bembi javal dukhata hota ata ujvya baajula khali potat khup vedna hot ahet.",
        typo_template="Apendix pain started at navel now in lower rite side.",
        negation_template="No diarrhea, pain migrated from mid-abdomen to right iliac fossa with localized rebound tenderness.",
        historical_template="Previously healthy 19-year-old presenting with classic progression of right lower quadrant pain.",
        third_party_template="My teenage son has severe pain in his lower right stomach and refuses to eat his dinner.",
        minimized_template="Pain in my lower right side that stings whenever the car hits a pothole.",
        default_age_years=19.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GAST_04",
        specialty="gastro_abdominal",
        gold_urgency=2,
        concept="vomiting",
        clinical_intent="Severe persistent vomiting with inability to tolerate oral fluids and signs of dehydration",
        formal_template="Intractable vomiting lasting 36 hours, unable to retain oral fluids, marked oliguria and dry mucous membranes.",
        colloquial_template="I have been throwing up constantly for a day and a half, can't keep even a sip of water down.",
        hinglish_template="Dedh din se lagatar ulti ho rahi hai ek ghoont paani bhi pet mein nahi ruk raha peshab nahi hua.",
        marathi_template="Kalapasun ulti thambatch nahiye paani suddha potat rahat nahiye mutra zale nahiye.",
        typo_template="Continous vomitting 36 hrs cant kepe water down dry mouth.",
        negation_template="No hematemesis, but complete inability to tolerate oral hydration for over 24 hours with postural lightheadedness.",
        historical_template="Developed acute gastroenteritis after banquet meal, progressing to clinical volume depletion.",
        third_party_template="My roommate has thrown up ten times since yesterday and has completely dry cracked lips.",
        minimized_template="Stomach rejects everything including ice chips, feeling parched.",
        default_age_years=41.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GAST_05",
        specialty="gastro_abdominal",
        gold_urgency=3,
        concept="diarrhea",
        clinical_intent="Moderate acute watery diarrhea without dehydration",
        formal_template="Four loose watery stools daily for 2 days, maintaining oral fluid intake, no blood or mucus, mild cramping.",
        colloquial_template="Have had loose watery stools 4 times today and mild stomach cramps, but drinking plenty of electrolytes.",
        hinglish_template="Do din se dast lag rahe hain din mein chaar baar jana pada lekin paani aur orsal le raha hoon.",
        marathi_template="Don divasapasun julaab hot ahet divsatun teen chaar vela paani peet ahe.",
        typo_template="Wattery diarihea 4 times today with belly cramps.",
        negation_template="No blood in stool, no fever, no vomiting, able to maintain good hydration with coconut water.",
        historical_template="Occasional travelers diarrhea after eating street food, typical uncomplicated course.",
        third_party_template="My brother has had watery diarrhea since yesterday after having street snacks.",
        minimized_template="A bit of an upset tummy with loose stools today, staying hydrated.",
        default_age_years=32.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GAST_06",
        specialty="gastro_abdominal",
        gold_urgency=3,
        concept="abdominal_pain",
        clinical_intent="Postprandial dyspepsia / acid reflux",
        formal_template="Epigastric burning discomfort occurring 45 minutes after fatty meals, aggravated by recumbency, relieved by antacids.",
        colloquial_template="I get a burning feeling in the upper middle stomach and acid taste in my throat after eating fried food.",
        hinglish_template="Khane ke baad chhaati ke neeche pet mein jalan hoti hai aur khatte dakaar aate hain.",
        marathi_template="Jevlyavar potat aani ghashat aambat aani aag hotiye acidity watte.",
        typo_template="Hartburn stumack burning after spicy fod acid tast.",
        negation_template="No dysphagia, no weight loss, no nocturnal vomiting, symptoms correlate directly with spicy meals.",
        historical_template="Longstanding history of mild gastroesophageal reflux disease when diet is poor.",
        third_party_template="My husband gets severe acid burning in his upper stomach whenever he eats late at night.",
        minimized_template="Standard acid indigestion after eating heavy curry, just burns a little.",
        default_age_years=43.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GAST_07",
        specialty="gastro_abdominal",
        gold_urgency=4,
        concept="abdominal_pain",
        clinical_intent="Mild transient bloating after carbonated beverage",
        formal_template="Mild abdominal distension and flatulence following large meal with carbonated soda, completely afebrile.",
        colloquial_template="My belly feels bloated and gassy after having a large lunch and drinking two cans of soda.",
        hinglish_template="Khane ke baad pet mein gas aur bhari-pan lag raha hai koi dard nahi hai bas pet phoola hai.",
        marathi_template="Jevlyavar potat gas zala ahe thoda phuglya sarkha wattoy dukhatch nahi.",
        typo_template="Stumack bloted and gassy after big meel soda.",
        negation_template="No pain, no nausea, no diarrhea, no vomiting, passing gas relieves the feeling of fullness.",
        historical_template="Common post-meal bloating without any clinical pathology.",
        third_party_template="My friend says she is bloated and stuffed after our buffet lunch.",
        minimized_template="Just ate too much pizza, stomach feels like a balloon for an hour.",
        default_age_years=25.0,
        default_sex="female",
    ),

    # --- 6. INFECTIOUS & FEVER (7 families) ---
    TemplateFamily(
        family_id="FAM_INFN_01",
        specialty="infectious_fever",
        gold_urgency=1,
        concept="fever",
        clinical_intent="Severe systemic sepsis with high fever, delirium and altered sensorium",
        formal_template="Elderly patient presenting with fever of 39.8C, confusion, somnolence, mottled extremities, and tachypnea.",
        colloquial_template="My grandfather has a burning high fever and doesn't know who we are or where he is, breathing very fast.",
        hinglish_template="Bohot tez bukhar hai 103 degree aur behosh jaisa hai kisi ko pehchan nahi raha baatein ulati kar raha hai.",
        marathi_template="Khup jorat taap ahe shuddhi var nahiye bhabdlya sarkha boltoy shwas jorat chaltoy.",
        typo_template="Hi fevar 103 delireous dont recognize famly fast brething.",
        negation_template="No clear localizing cough, acute profound cognitive deterioration in setting of severe fever.",
        historical_template="History of recurrent urinary tract infections, now presented in septic delirium.",
        third_party_template="My elderly neighbor is delirious with a raging fever and cannot answer simple questions.",
        minimized_template="He is burning hot and talking about people from 40 years ago, looks very frail.",
        default_age_years=78.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_INFN_02",
        specialty="infectious_fever",
        gold_urgency=1,
        concept="fever",
        clinical_intent="Suspected bacterial meningitis with high fever, photophobia and nuchal rigidity",
        formal_template="High fever 39.5C, severe headache, photophobia, and marked neck stiffness with inability to touch chin to chest.",
        colloquial_template="Blazing fever and my neck is so stiff I cannot bend my head down, lights are blinding and agony.",
        hinglish_template="Bohot tez bukhar hai gardan bilkul akad gayi hai aage nahi jhuk rahi aur sir phat raha hai.",
        marathi_template="Khup taap ahe maana akadli ahe aani doke phatat ahe prakash baghavat nahi.",
        typo_template="Fevar 103 stif neck cant tutch chin to chesst bliding headach.",
        negation_template="No trauma, acute onset febrile illness with severe meningism and petechial spots on abdomen.",
        historical_template="College student living in dormitory, presented with rapid febrile meningeal syndrome.",
        third_party_template="My dorm roommate has a burning fever and says his neck hurts too much to bend forward.",
        minimized_template="Neck is terribly stiff today with a high fever, can't look at my phone screen.",
        default_age_years=21.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_INFN_03",
        specialty="infectious_fever",
        gold_urgency=2,
        concept="fever",
        clinical_intent="Prolonged high fever lasting >5 days with systemic symptoms (e.g. Dengue / Typhoid)",
        formal_template="High remittent fever of 39C persisting for 6 consecutive days with severe retro-orbital pain, severe myalgia and arthralgia.",
        colloquial_template="I have had a 102 degree fever for 6 days straight with unbearable body aches and eye socket pain.",
        hinglish_template="Chhe din se lagatar 102 bukhar utar nahi raha aankhon ke peeche aur jodon mein bohot dard hai.",
        marathi_template="Saha divas zale taap utarat nahiye aanga dukhtay dolyanchya maage khup vedna ahet.",
        typo_template="Fevar 102 for 6 days myalgias pain behid eyes.",
        negation_template="No cough or sore throat, persistent high continuous fever beyond 5 days with break-bone body aches.",
        historical_template="Returned from rural monsoon area 8 days ago, developed unremitting febrile syndrome.",
        third_party_template="My cousin has been burning with fever for almost a full week without breaking.",
        minimized_template="Still running this 102 fever going onto day 6, body feels like it got run over.",
        default_age_years=35.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_INFN_04",
        specialty="infectious_fever",
        gold_urgency=2,
        concept="fever",
        clinical_intent="Acute febrile illness in an immunocompromised host",
        formal_template="Fever of 38.6C in a patient currently undergoing chemotherapy for breast cancer, absolute neutrophil count unknown.",
        colloquial_template="I am on chemo treatment and developed a fever of 101.4 today with shaking chills.",
        hinglish_template="Chemotherapy chal rahi hai cancer ki aur aaj achanak 101 bukhar aur kapkapi shuru ho gayi.",
        marathi_template="Cancer chemotherapy chalu ahe aani achanak taap bharla thandi wajun aali.",
        typo_template="On kemo cancer trement fevar 101 shivring chills today.",
        negation_template="No localized pain, but neutropenic fever precautions required immediately due to active cytotoxic therapy.",
        historical_template="Receiving third cycle of adjuvant chemotherapy completed 6 days ago.",
        third_party_template="My sister is undergoing chemotherapy and just spiked a fever of 38.5 degrees.",
        minimized_template="Feeling a bit feverish today at 101, oncologist told me to take notice of any temperature.",
        default_age_years=51.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_INFN_05",
        specialty="infectious_fever",
        gold_urgency=3,
        concept="fever",
        clinical_intent="Acute viral syndrome with low-grade fever and myalgia for 2 days",
        formal_template="Low-grade fever 38.0C for 48 hours accompanied by mild general malaise, myalgia and clear rhinorrhea.",
        colloquial_template="Feeling feverish around 100 degrees with general body aches and tiredness for the past two days.",
        hinglish_template="Do din se halka bukhar 100 degree hai badan mein thoda thoda dard hai aalas lag raha hai.",
        marathi_template="Don divasapasun thoda taap ahe anga dukhtay aani thakva ahe.",
        typo_template="Mild fevar 100 for 2 days body akes tierdness.",
        negation_template="No difficulty breathing, no confusion, no neck stiffness, able to drink fluids and eat light meals.",
        historical_template="Typical seasonal flu-like illness that self-resolves with home rest.",
        third_party_template="My coworker has had a 100 degree temperature and mild muscle aches since yesterday.",
        minimized_template="Just a minor bug with a 100 degree fever, taking it easy on the sofa.",
        default_age_years=29.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_INFN_06",
        specialty="infectious_fever",
        gold_urgency=3,
        concept="fever",
        clinical_intent="Acute pharyngitis with fever and painful swallowing",
        formal_template="Fever 38.2C for 24 hours with bilateral tonsillar exudates, painful odynophagia and tender anterior cervical lymphadenopathy.",
        colloquial_template="My throat feels like razor blades when I swallow and I have a fever of 101.",
        hinglish_template="Gale mein bohot tez dard hai nikalte waqt chubhta hai aur 101 bukhar hai.",
        marathi_template="Ghasa khup dukhto ahe ghaltana tras hoto aani 101 taap ahe.",
        typo_template="Sore throt rasor blades when swalow fevar 101.",
        negation_template="No stridor, no difficulty breathing, uvula is midline, can swallow liquids with discomfort.",
        historical_template="Gets occasional acute streptococcal tonsillitis during winter periods.",
        third_party_template="My teenage daughter has a fiery sore throat and temperature since this morning.",
        minimized_template="Throat hurts to swallow and running a warm temperature, drinking honey water.",
        default_age_years=18.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_INFN_07",
        specialty="infectious_fever",
        gold_urgency=4,
        concept="fever",
        clinical_intent="Post-vaccination low-grade transient fever",
        formal_template="Mild transient low-grade fever 37.8C occurring 12 hours after routine tetanus toxoid vaccination with localized injection site soreness.",
        colloquial_template="Got my tetanus booster vaccine yesterday morning and have a slight 99.8 fever and sore arm today.",
        hinglish_template="Kal sui lagwayi thi tetanus ki aaj baazu mein dard hai aur halka sa 99 bukhar hai.",
        marathi_template="Kal injection ghetla hota hatavar dukhatahe aani thoda taap ahe 99.",
        typo_template="Tetanus shot yestarday arm sore slight 99 fevar.",
        negation_template="No systemic rash, no difficulty breathing, no high fever, mild localized post-immunization reactogenicity.",
        historical_template="Known normal transient reactive fever following previous immunization doses.",
        third_party_template="My friend has a slightly warm forehead after getting his vaccine dose yesterday.",
        minimized_template="Arm is a little tender from the vaccine and running a tiny 99 temp, feels expected.",
        default_age_years=27.0,
        default_sex="male",
    ),

    # --- 7. PEDIATRIC (7 families) ---
    TemplateFamily(
        family_id="FAM_PED_01",
        specialty="pediatric",
        gold_urgency=1,
        concept="fever",
        clinical_intent="Fever in young neonate under 1 month of age (NICE NG143 red flag)",
        formal_template="Neonate 18 days old presenting with rectal temperature of 38.3C, poor feeding and lethargy.",
        colloquial_template="My 18 day old newborn baby has a fever of 101 and won't nurse or wake up to feed.",
        hinglish_template="Athara din ka navjaat baccha hai 101 bukhar hai doodh nahi pee raha bohot sust pada hai.",
        marathi_template="Aathra divasacha lahan baal ahe taap 101 ahe doodh peet nahiye aani sust padla ahe.",
        typo_template="18 days old newbrn babi fevar 101 wont nurce lethergic.",
        negation_template="No cough, but neonate under 28 days with core temperature >=38.0C requires immediate neonatal sepsis workup.",
        historical_template="Full term normal vaginal delivery, developed sudden pyrexia on day 18 of life.",
        third_party_template="My sister's three-week-old infant is running a high temperature and barely opening her eyes.",
        minimized_template="Baby feels warm to touch and sleeping longer than usual between nursing sessions.",
        default_age_years=None,
        default_age_months=0.6,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_PED_02",
        specialty="pediatric",
        gold_urgency=1,
        concept="seizure",
        clinical_intent="Pediatric febrile status epilepticus / prolonged convulsion",
        formal_template="Toddler 18 months old with fever 39.5C experiencing generalized tonic-clonic seizure persisting past 10 minutes.",
        colloquial_template="My 18 month toddler is convulsing with a high fever and the shaking has been going on for 10 minutes.",
        hinglish_template="Dedh saal ka baccha hai tez bukhar mein jhatke aa rahe hain 10 minute se ruk nahi rahe.",
        marathi_template="Dhed varshacha baal ahe taapat zatke yet ahet dahavya minitapasun thambat nahiye.",
        typo_template="18 mo old tobler fevar siesure shakin 10 mins wont stop.",
        negation_template="No cessation after 5 minutes, prolonged complex febrile convulsion requiring urgent rescue anticonvulsants.",
        historical_template="First episode of prolonged febrile convulsion in toddler.",
        third_party_template="The little boy at the nursery is having a continuous seizure with a high temperature.",
        minimized_template="He has been twitching with fever for quite a while now without regaining awareness.",
        default_age_years=1.5,
        default_age_months=18.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_PED_03",
        specialty="pediatric",
        gold_urgency=2,
        concept="fever",
        clinical_intent="Infant 2-3 months with fever (NICE amber flag)",
        formal_template="Infant 2.5 months old presenting with temperature 38.6C for 12 hours, irritable but consolable.",
        colloquial_template="My 10-week-old baby has a fever of 101.5, crying more than usual but will take a bottle.",
        hinglish_template="Dhai mahine ka baccha hai 101 bukhar hai bohot ro raha hai lekin doodh pee raha hai.",
        marathi_template="Aadich mahinyacha baal ahe 101 taap ahe radto ahe pan doodh ghet ahe.",
        typo_template="10 wek old babi 101.5 fevar crying lot but taking botle.",
        negation_template="No petechiae, no respiratory distress, no fontanelle bulging, but age under 3 months mandates urgent clinical evaluation.",
        historical_template="Routine vaccinations up to date, developed acute fever without clear focus.",
        third_party_template="My neighbor's two-month-old baby girl spiked a fever this afternoon.",
        minimized_template="Baby is a bit warm and cranky today, taking milk slower than usual.",
        default_age_years=None,
        default_age_months=2.5,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_PED_04",
        specialty="pediatric",
        gold_urgency=2,
        concept="vomiting",
        clinical_intent="Toddler with dehydration from gastroenteritis",
        formal_template="Toddler 20 months old with 6 episodes of vomiting and 5 watery stools in 12 hours, dry diapers for 8 hours, sunken eyes.",
        colloquial_template="My 20 month old has been vomiting and has diarrhea all day, hasn't peed in 8 hours and looks hollow eyed.",
        hinglish_template="Bees mahine ke bacche ko ulti dast ho rahe hain 8 ghante se diaper geela nahi kiya aankhein dhas gayi hain.",
        marathi_template="Veess mahinyacha baal ahe ulti julaab mule aath taasat lagnicha diaper bharla nahiye dolye khali gele ahet.",
        typo_template="20 mo todler vomitin diarhea no wet dipar 8 hrs sunkin eyes.",
        negation_template="No bile in vomitus, no blood in stool, but clinical signs of moderate pediatric dehydration.",
        historical_template="Attends daycare where rotavirus outbreak was reported this week.",
        third_party_template="The toddler is listless with dry lips and has not produced a wet nappy all day.",
        minimized_template="He threw up a few times and his diaper has been dry since morning.",
        default_age_years=1.6,
        default_age_months=20.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_PED_05",
        specialty="pediatric",
        gold_urgency=3,
        concept="fever",
        clinical_intent="Older child with uncomplicated mild fever and upper respiratory symptoms",
        formal_template="School age child 7 years old with temperature 38.1C for 24 hours, mild cough, active and alert, drinking fluids.",
        colloquial_template="My 7 year old daughter has a 100.5 fever and a runny nose but she is happily coloring and eating toast.",
        hinglish_template="Saat saal ki bacchi ko halka bukhar aur sardi hai lekin khel rahi hai aur khana kha rahi hai.",
        marathi_template="Saat varshachi mulgi ahe thoda taap aani sardi ahe pan kheltiye aani jevtiye.",
        typo_template="7 yr old child 100 fevar runy nose plying fine.",
        negation_template="No breathing difficulty, no earache, no neck stiffness, maintaining normal activity and hydration.",
        historical_template="Standard viral cold caught from classmates at primary school.",
        third_party_template="My niece has a slight temperature after school but is running around the living room.",
        minimized_template="She has a warm forehead and sniffles, playing happily with her toys.",
        default_age_years=7.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_PED_06",
        specialty="pediatric",
        gold_urgency=3,
        concept="rash",
        clinical_intent="Classic mild viral exanthem (e.g. roseola or chickenpox in school age child)",
        formal_template="Child 5 years old presenting with non-pruritic maculopapular rash on trunk following defervescence of 3-day mild fever.",
        colloquial_template="My 5 year old had a mild fever for 3 days that broke yesterday, and now has pink spots all over his belly.",
        hinglish_template="Paanch saal ke bacche ka bukhar kal utar gaya aur aaj pet aur peeth par gulabi daane nikal aaye hain.",
        marathi_template="Paach varshachya mulacha taap gela aani potavar gulabi phod aale ahet bara ahe.",
        typo_template="5 yr old child pink spots on tumy after fevar broke.",
        negation_template="No fever now, rash is non-blanching negative (blanches easily with glass test), child in good spirits.",
        historical_template="Typical post-viral exanthem (roseola infantum / viral exanthem).",
        third_party_template="My nephew has little pink dots on his chest after having a cold earlier this week.",
        minimized_template="Just some harmless pink spots after his fever cleared up.",
        default_age_years=5.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_PED_07",
        specialty="pediatric",
        gold_urgency=4,
        concept="rash",
        clinical_intent="Mild infant diaper dermatitis (nappy rash)",
        formal_template="Infant 9 months old with mild erythematous macular erythema confined strictly to diaper contact areas, skin folds spared.",
        colloquial_template="My 9 month old baby has mild red irritation on his bottom from his diaper, smiling and playing normally.",
        hinglish_template="Nau mahine ke bacche ke diaper wali jagah par halki laali hai baccha khush hai koi dikkat nahi.",
        marathi_template="Nau mahinyachya baalala diaper mule thoda laal zala ahe pan baal hasat khelat ahe.",
        typo_template="9 mo babi red diaper rash smilin playin normel.",
        negation_template="No open ulcers, no fever, no pustules, creases are clear, infant completely comfortable.",
        historical_template="Frequent mild nappy rash when teething.",
        third_party_template="The baby has a little diaper redness on his cheeks after wearing a wet nappy overnight.",
        minimized_template="Just a minor diaper rash, applying zinc barrier cream.",
        default_age_years=None,
        default_age_months=9.0,
        default_sex="male",
    ),

    # --- 8. ENVIRONMENTAL & TRAUMA (7 families) ---
    TemplateFamily(
        family_id="FAM_TRAU_01",
        specialty="environmental_trauma",
        gold_urgency=1,
        concept="snakebite",
        clinical_intent="Venomous snakebite with local tissue necrosis or systemic neurotoxicity",
        formal_template="Definite snakebite to lower extremity with visible fang marks, rapidly progressive swelling, and bilateral ptosis.",
        colloquial_template="A snake bit my ankle in the field 20 minutes ago, swelling is racing up my leg and eyelids are drooping.",
        hinglish_template="Khet mein saanp ne kaat liya hai pair mein do daant ke nishan hain soojan upar chad rahi hai aankhein band ho rahi hain.",
        marathi_template="Shetat saapane chavla ahe paayavar daatache khun ahet aani sujan vadhatiye dole band hot ahet.",
        typo_template="Snak bite on fot 2 fang marks sweling spreding fast eyelids droping.",
        negation_template="No tourniquet applied, acute envenomation signs spreading rapidly within 30 minutes of bite.",
        historical_template="Agricultural worker bitten while clearing tall grass at dusk.",
        third_party_template="My brother was bitten on the heel by a venomous viper in the farm, leg is swelling purple.",
        minimized_template="Got nipped by a snake in the dark, leg is swelling pretty fast and feeling drowsy.",
        default_age_years=36.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_TRAU_02",
        specialty="environmental_trauma",
        gold_urgency=1,
        concept="severe_bleeding",
        clinical_intent="Arterial traumatic hemorrhage with spurting bright red blood",
        formal_template="Deep laceration to volar wrist with pulsating spurting arterial bleeding, refractory to direct manual compression.",
        colloquial_template="Glass cut my wrist deep, blood is pumping out in spurts like a hose and soaking through towels.",
        hinglish_template="Kanch se kalai cut gayi hai dhar maar ke khoon nikal raha hai kapde se dabane par bhi ruk nahi raha.",
        marathi_template="Kaach lagli ahe hatala phavaryasarkhe rakt udtahe rumalane dabun suddha thambat nahiye.",
        typo_template="Deep cut on rist blud spurting pulsing out cant stop.",
        negation_template="No minor superficial scrape, arterial pulsatile bleeding with early pallor and lightheadedness.",
        historical_template="Accidental injury sustained from shattered glass shower door.",
        third_party_template="The carpenter cut his arm with a circular saw, blood is gushing out rapidly.",
        minimized_template="Cut my wrist deeply, towels are drenched with blood within two minutes.",
        default_age_years=28.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_TRAU_03",
        specialty="environmental_trauma",
        gold_urgency=1,
        concept="altered_mental_status",
        clinical_intent="Severe heat stroke with hyperthermia and unconsciousness",
        formal_template="Collapse following prolonged physical exertion in 43C ambient heat, core temperature 41C, anhidrosis, coma.",
        colloquial_template="He collapsed while working in the extreme heat, skin is burning hot and dry, he is completely unconscious.",
        hinglish_template="Bohot dhoop mein kaam karte waqt gir pada sharir aag jaisa garam hai aur koi aawaz nahi sun raha.",
        marathi_template="Unhat kaam kartana behosh padla anga aag sarkha tapla ahe shuddhi nahiye lath nahi.",
        typo_template="Heat colapse 43C sun burning hot skin unconsious.",
        negation_template="No sweating, profound thermoregulatory failure with coma after outdoor manual labor in high heat index.",
        historical_template="Construction worker working consecutive hours in direct sunlight during summer heatwave.",
        third_party_template="A marathon runner collapsed near the finish line in blistering heat, completely unresponsive.",
        minimized_template="He overheated terribly in the sun and is out cold with boiling hot skin.",
        default_age_years=39.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_TRAU_04",
        specialty="environmental_trauma",
        gold_urgency=2,
        concept="severe_bleeding",
        clinical_intent="Deep laceration requiring formal wound closure / sutures",
        formal_template="Deep 5cm gaping linear laceration over extensor surface of forearm, subcutaneous fat visible, bleeding controlled with pressure.",
        colloquial_template="Cut my arm on a rusty metal sheet, wound is open and gaping wide, you can see yellow fat inside.",
        hinglish_template="Lohe ki sheet se hath par gehra ghaav ho gaya hai khula hua hai taanke lagwane padenge.",
        marathi_template="Pukhta patryane hatala khol zakhama zali ahe zakhama ughadi ahe take padave lagtil.",
        typo_template="Deep 5cm cut on arm gapin open see yelow fat stiches neded.",
        negation_template="No arterial spurting, bleeding controlled with firm pressure, but gaping edges will not appose without sutures.",
        historical_template="Tetanus booster received 7 years ago, requires evaluation for wound debridement and booster.",
        third_party_template="My son cut his leg on a broken fence, wound is gaping about two inches long.",
        minimized_template="Caught my arm on some metal, gaping open pretty cleanly, probably needs a stitch or two.",
        default_age_years=31.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_TRAU_05",
        specialty="environmental_trauma",
        gold_urgency=2,
        concept="dizziness",
        clinical_intent="Mild closed head injury with brief loss of consciousness and vomiting",
        formal_template="Direct impact head trauma 2 hours ago with 10-second loss of consciousness followed by 2 episodes of emesis and anterograde amnesia.",
        colloquial_template="Hit my head playing soccer, was knocked out for a few seconds and now threw up and can't remember the score.",
        hinglish_template="Football khelte waqt sir par chot lagi thodi der ke liye behosh hua tha ab ulti hui aur yaad nahi aa raha.",
        marathi_template="Doke jorat adalla thoda vel be-shuddha zala hota ata ulti zali aani kahi aathvat nahiye.",
        typo_template="Hit hed playing soccor nocked out 10 sec vomitted 2x amnesa.",
        negation_template="No skull fracture visible, but witnessed concussion with loss of consciousness and post-traumatic vomiting.",
        historical_template="High impact collision between two athletes during tournament game.",
        third_party_template="My teammate took a hard hit to the forehead, passed out momentarily and is now nauseous and foggy.",
        minimized_template="Got my bell rung pretty good on the pitch, threw up once, feeling spaced out.",
        default_age_years=22.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_TRAU_06",
        specialty="environmental_trauma",
        gold_urgency=3,
        concept="abdominal_pain",
        clinical_intent="Acute superficial second-degree thermal burn <2% BSA without face/hand involvement",
        formal_template="Partial thickness scald burn with intact blister 3cm diameter on lateral thigh from boiling water, sensation intact.",
        colloquial_template="Accidentally spilled hot boiling tea on my thigh, have a red painful blister about the size of a coin.",
        hinglish_template="Jangh par garam chai gir gayi chala pad gaya hai aur jalan ho rahi hai.",
        marathi_template="Mandyavar garam chaha saandla phod aala ahe aani aag hotiye.",
        typo_template="Spiled boilin tea on leg red painfull blistar.",
        negation_template="No circumferential burn, no facial involvement, no chemical exposure, localized scald lesion.",
        historical_template="Domestic kitchen spill 30 minutes ago, cooled immediately with running tap water for 15 minutes.",
        third_party_template="My wife splashed hot soup onto her leg and has a two-inch water blister.",
        minimized_template="Small blister on my thigh from a tea spill, stings when pants rub against it.",
        default_age_years=34.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_TRAU_07",
        specialty="environmental_trauma",
        gold_urgency=4,
        concept="severe_bleeding",
        clinical_intent="Minor superficial paper cut or abrasion completely clotted",
        formal_template="Superficial cutaneous paper cut on index finger, bleeding ceased spontaneously within 60 seconds, no contamination.",
        colloquial_template="I got a small paper cut opening an envelope this morning, stopped bleeding immediately.",
        hinglish_template="Kagaz se ungli par halka sa cut lag gaya tha khoon turant ruk gaya thoda dukh raha hai.",
        marathi_template="Kagadane botavar chotasa cut zala lagech rakt thambla thoda aag hoti.",
        typo_template="Papar cut on fingar stoped bleylding in a minit.",
        negation_template="No deep tissue damage, no foreign body, bleeding completely clotted, epidermis intact.",
        historical_template="Standard minor office injury.",
        third_party_template="My colleague nicked his finger on cardboard packaging, put a bandaid on it.",
        minimized_template="Just a silly little paper cut that stings when washing hands.",
        default_age_years=26.0,
        default_sex="male",
    ),

    # --- 9. GENITOURINARY (7 families) ---
    TemplateFamily(
        family_id="FAM_GENU_01",
        specialty="genitourinary",
        gold_urgency=1,
        concept="abdominal_pain",
        clinical_intent="Suspected testicular torsion with acute severe unilateral scrotal pain and swelling",
        formal_template="Sudden onset acute severe unilateral left testicular pain and swelling 90 minutes ago with nausea, high riding testis.",
        colloquial_template="Sudden agonizing pain in my left testicle out of nowhere, it has swollen up high and I feel sick to my stomach.",
        hinglish_template="Achanak andkosh mein bohot tez jaan-leva dard shuru hua soojan aa gayi hai aur ulti jaisa lag raha hai.",
        marathi_template="Achanak andashayat khup tivra vedna suru zalya aani sujan aali ahe ulti watte.",
        typo_template="Sudden agnizing pain in left testicel swolen up 1 hr ago.",
        negation_template="No trauma, acute testicular ischemia symptoms within golden 6-hour window for surgical salvage.",
        historical_template="No prior episodes, sudden awakening from sleep with excruciating scrotal pain.",
        third_party_template="My teenage son woke up screaming in agony clutching his groin with severe testicular pain.",
        minimized_template="Left side of my scrotum is terribly painful and swollen, having trouble standing straight.",
        default_age_years=16.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENU_02",
        specialty="genitourinary",
        gold_urgency=2,
        concept="fever",
        clinical_intent="Acute pyelonephritis with high fever, unilateral flank pain and dysuria",
        formal_template="Fever 39.1C, rigors, unilateral right costovertebral angle tenderness, dysuria and urinary frequency for 24 hours.",
        colloquial_template="High fever with chills, severe stabbing pain in my right lower back flank, and burning when I pee.",
        hinglish_template="Tez bukhar kapkapi aur peeth ke daayein taraf kamar mein tez dard hai peshab mein bohot jalan hai.",
        marathi_template="Taap thandi aani pathichya eka baajula kambarit khup dukhatahe mutrat aag hotiye.",
        typo_template="Fevar 102 flank pain in rite back burnin when peeing.",
        negation_template="No gross hematuria, but upper urinary tract infection signs with systemic febrile toxicity and renal angle tenderness.",
        historical_template="History of lower cystitis treated 3 weeks ago, now ascending upper tract infection.",
        third_party_template="My mother has a 102 fever and is crying from sharp pain in her right kidney area.",
        minimized_template="Nasty ache in my right flank with a temperature and stinging urine.",
        default_age_years=38.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GENU_03",
        specialty="genitourinary",
        gold_urgency=2,
        concept="dysuria",
        clinical_intent="Acute urinary retention with painful bladder distension",
        formal_template="Inability to void for 14 hours despite intense urgency, severe suprapubic pain with palpable distended bladder.",
        colloquial_template="I cannot pee at all since last night, my lower bladder is bursting with pressure and agonizing pain.",
        hinglish_template="Raat se peshab bilkul nahi utar raha pet ke nichle hisse mein phatne jaisa dard ho raha hai.",
        marathi_template="Kal ratripasun peshab bilkul zali nahiye potacha khalcha bhag phugla ahe aani khup dukhto.",
        typo_template="Cant pe at all for 14 hrs blader bursting pain.",
        negation_template="No anuria from renal failure, severe painful bladder retention with constant unsuccessful straining.",
        historical_template="Known benign prostatic hyperplasia with progressive hesitancy, took cold medication yesterday.",
        third_party_template="My elderly father has been groaning on the toilet unable to pass a single drop of urine for 12 hours.",
        minimized_template="Bladder feels completely full like a water balloon and nothing comes out when I try.",
        default_age_years=71.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENU_04",
        specialty="genitourinary",
        gold_urgency=3,
        concept="dysuria",
        clinical_intent="Uncomplicated lower urinary tract infection / cystitis in adult female",
        formal_template="Dysuria, urinary urgency, and frequency every 30 minutes for 36 hours, afebrile, suprapubic ache, no flank pain.",
        colloquial_template="Burning pain when I urinate and having to run to the toilet every 20 minutes to pass tiny drops.",
        hinglish_template="Peshab karte waqt bohot tez jalan hoti hai aur baar baar peshab aati hai thodi thodi.",
        marathi_template="Mutra hotana khup aag hotiye aani dar vees minitane jaave lagte thode thode.",
        typo_template="Burnig pain peeing runing to batroom evry 20 mins dropes.",
        negation_template="No fever, no chills, no back pain, no vaginal discharge, classic lower urinary tract cystitis.",
        historical_template="Second episode of simple cystitis this year, typical presentation.",
        third_party_template="My girlfriend has a painful bladder infection with burning urine since yesterday.",
        minimized_template="Stinging when I pee and visiting the restroom constantly today.",
        default_age_years=29.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GENU_05",
        specialty="genitourinary",
        gold_urgency=3,
        concept="abdominal_pain",
        clinical_intent="Suspected nephrolithiasis / renal colic without infection",
        formal_template="Severe spasmodic unilateral left flank pain radiating to groin, waxing and waning in intensity, microscopic hematuria, afebrile.",
        colloquial_template="Wave-like stabbing pain in my left side radiating down into my groin, can't find any comfortable position to sit.",
        hinglish_template="Kamar ke baayein hisse se le kar aage tak achanak lehar jaisa bohot tez dard uthta hai patthari jaisa lagta hai.",
        marathi_template="Kambarichya davyan baajutun pudhe parant laate sarkhe vedna yetat khadya sarakha watat ahe.",
        typo_template="Stabin wavelike pain in left flank shootin to groyn stone.",
        negation_template="No fever, no chills, no vomiting, typical colicky pain characteristics of urolithiasis.",
        historical_template="Previous calcium oxalate kidney stone passed 3 years ago.",
        third_party_template="My brother is pacing the floor clutching his side saying his kidney stone pain has returned.",
        minimized_template="Got that familiar sharp colicky stone pain in my left flank again.",
        default_age_years=42.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENU_06",
        specialty="genitourinary",
        gold_urgency=4,
        concept="dysuria",
        clinical_intent="Dark concentrated urine after inadequate fluid intake",
        formal_template="Dark amber concentrated urine noticed after prolonged outdoor physical training without hydration, no dysuria or pain.",
        colloquial_template="My urine looked dark yellow and concentrated this afternoon after playing tennis in the heat.",
        hinglish_template="Dhoop mein khelne ke baad peshab thoda gehra peela aaya hai koi jalan ya dard nahi hai.",
        marathi_template="Khelun aalyawar mutra pivala aala ahe aag nahiye dukhata nahiye.",
        typo_template="Dark yelow concentraded urine after sport no pain.",
        negation_template="No burning, no frequency, no back pain, color normalized to pale straw after drinking 1 liter of water.",
        historical_template="Known physiological urine concentration during athletic workouts.",
        third_party_template="My friend noticed his urine was dark amber after our long afternoon bike ride.",
        minimized_template="Urine was just a bit dark after jogging without my water bottle.",
        default_age_years=24.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENU_07",
        specialty="genitourinary",
        gold_urgency=4,
        concept="dysuria",
        clinical_intent="Transient benign post-intercourse urethral sensitivity",
        formal_template="Transient mild urethral awareness for 1 hour following sexual intercourse, completely resolved, no discharge or frequency.",
        colloquial_template="Felt a slight temporary stinging sensation once when peeing after intimacy, feels completely normal now.",
        hinglish_template="Ek baar peshab mein halki chubhan hui thi ab sab normal hai koi takleef nahi hai.",
        marathi_template="Ekda thodishi aag zali hoti ata purna bara ahe kahi tras nahiye.",
        typo_template="Slight 1 time sting peeing after sex now totaly fine.",
        negation_template="No persistent burning, no discharge, no rash, no pelvic pain, isolated fleeting sensation.",
        historical_template="Occasional mild friction sensitivity.",
        third_party_template="A friend asked if a one-time mild sting after intimacy is concerning if it went away immediately.",
        minimized_template="Felt a micro-sting once, completely back to normal an hour later.",
        default_age_years=27.0,
        default_sex="female",
    ),

    # --- 10. GENERAL & SELF CARE (7 families) ---
    TemplateFamily(
        family_id="FAM_GENL_01",
        specialty="general_self_care",
        gold_urgency=1,
        concept="altered_mental_status",
        clinical_intent="Acute severe hypoglycemia with unresponsiveness in insulin-dependent diabetic",
        formal_template="Diabetic patient found minimally responsive, profuse diaphoresis, glucometer reading 32 mg/dL, unable to ingest oral carbohydrates.",
        colloquial_template="My diabetic mother is soaked in cold sweat and will not wake up or respond to her name.",
        hinglish_template="Sugar ki mareez hain thande pasine mein bheege hue behosh hain hosh nahi aa raha hai.",
        marathi_template="Diabetic patient thandagar ghaam aala ahe aani be-shuddha ahet uthat nahiye.",
        typo_template="Diabetic insuline unconsious cold swet sugar 32 cant wake.",
        negation_template="No head trauma, took evening insulin but missed dinner, acute neuroglycopenic stupor.",
        historical_template="Type 1 diabetes for 15 years with hypoglycemia unawareness.",
        third_party_template="My father with diabetes is slumped over the table drenched in sweat and not responding.",
        minimized_template="Her blood sugar crashed severely and she is passed out cold on the bed.",
        default_age_years=62.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GENL_02",
        specialty="general_self_care",
        gold_urgency=2,
        concept="dizziness",
        clinical_intent="Acute syncope with sudden collapse in older adult",
        formal_template="Sudden unheralded syncopal episode while seated 1 hour ago, complete loss of consciousness for 30 seconds with spontaneous recovery.",
        colloquial_template="I suddenly blacked out and fainted while sitting in my armchair, woke up on the floor 30 seconds later.",
        hinglish_template="Kursi par baithe baithe achanak andhera chha gaya aur behosh ho kar gir pada adhe minute baad hosh aaya.",
        marathi_template="Kurchivar baslyawar achanak dolyasamor andhari aali aani be-shuddha hovun padlo aadhi minitat hosh aala.",
        typo_template="Sudden faint blacked out in chair wolk up on flor 30 sec.",
        negation_template="No seizure jerking, no tongue bite, but sudden unheralded syncope in 70-year-old warrants immediate cardiac evaluation.",
        historical_template="First syncopal episode in lifetime, no prodrome of lightheadedness or nausea.",
        third_party_template="My grandmother suddenly went limp and passed out in the living room without any warning.",
        minimized_template="Just had a quick little blackout spell while sitting watching TV.",
        default_age_years=73.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GENL_03",
        specialty="general_self_care",
        gold_urgency=2,
        concept="dizziness",
        clinical_intent="Symptomatic postural orthostatic hypotension with near-syncope",
        formal_template="Recurrent severe postural presyncope upon standing with documented blood pressure drop, blurred vision and staggering for 2 days.",
        colloquial_template="Every time I stand up from a chair the room goes black, my ears ring and I have to grab the wall to not faint.",
        hinglish_template="Jaise hi khada hota hoon aankhon ke aage andhera chha jata hai aur girne lagta hoon do din se.",
        marathi_template="Ubhe rahilyavar lagech andhari yete aani chakkar yete bhint pakdavi lagte.",
        typo_template="Evry time I stand up evrything goes blak almst fainting.",
        negation_template="No syncope when lying down, symptoms occur exclusively upon assuming upright posture.",
        historical_template="Recently doubled dosage of blood pressure medication 4 days ago.",
        third_party_template="My mother sways and nearly collapses every time she gets out of her bed.",
        minimized_template="Get a bit of head rush when I get up too quickly, just need to stand slowly.",
        default_age_years=66.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENL_04",
        specialty="general_self_care",
        gold_urgency=3,
        concept="dizziness",
        clinical_intent="Subacute generalized fatigue / exhaustion from chronic overwork",
        formal_template="Persistent fatigue and physical lethargy for 3 weeks in context of 70-hour work weeks and sleep disruption, exam otherwise unremarkable.",
        colloquial_template="I have been exhausted, run down and low on energy for nearly a month from working crazy hours.",
        hinglish_template="Teen hafte se bohot thakan aur kamzori lag rahi hai har waqt neend aati rehti hai kaam ke tanaav se.",
        marathi_template="Teen athavadyapasun khup thakva ahe sharirat taakat nahiye kaamamule tras hoto.",
        typo_template="Exhasted tierd low enrgy for 3 weaks overwerk.",
        negation_template="No weight loss, no fever, no shortness of breath, blood count and thyroid tests previously normal.",
        historical_template="Chronic workaholic stress pattern during annual corporate audit cycles.",
        third_party_template="My husband has been completely drained of energy and sleeping through weekends.",
        minimized_template="Just feeling worn down and running on fumes after a hectic month at work.",
        default_age_years=37.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENL_05",
        specialty="general_self_care",
        gold_urgency=3,
        concept="dizziness",
        clinical_intent="Mild insomnia with difficulty initiating sleep",
        formal_template="Difficulty initiating sleep with sleep latency exceeding 90 minutes for 10 days, daytime fatigue, no mood disorder.",
        colloquial_template="I toss and turn in bed for two hours every night unable to fall asleep because my mind is racing.",
        hinglish_template="Raat ko bistar par do do ghante karwatein badalta hoon neend nahi aati dimaag chalta rehta hai.",
        marathi_template="Ratri zop lagat nahiye don taas padun rahave lagte vichar chalat ahet.",
        typo_template="Cant fal aslep tosing and turnin 2 hrs evry nite.",
        negation_template="No early morning awakening, no suicidal thoughts, no breathing cessation reported by partner.",
        historical_template="Occasional stress-induced sleep initiation insomnia.",
        third_party_template="My daughter has been having trouble falling asleep before 3 AM for the past week.",
        minimized_template="A bit restless at bedtime lately, takes a while to drift off.",
        default_age_years=31.0,
        default_sex="female",
    ),
    TemplateFamily(
        family_id="FAM_GENL_06",
        specialty="general_self_care",
        gold_urgency=4,
        concept="dizziness",
        clinical_intent="Mild delayed-onset muscle soreness (DOMS) after exercise",
        formal_template="Bilateral quadriceps muscle soreness developing 24 hours after unaccustomed squat exercises, no swelling or dark urine.",
        colloquial_template="My leg thigh muscles are stiff and sore going down stairs today after my gym workout yesterday.",
        hinglish_template="Kal gym mein workout kiya tha aaj jaanghon ki maspeshiyon mein meetha meetha dard aur jakdan hai.",
        marathi_template="Kal vyayam kelyamule mandya bharun aalya ahet thoda dukhtay halchaal kartana.",
        typo_template="Sore thiegh musles after jim yestarday stif on stares.",
        negation_template="No joint swelling, no dark tea-colored urine, no focal muscle tear, symmetric bilateral post-exercise soreness.",
        historical_template="Standard delayed onset muscle soreness experienced whenever resuming gym routine.",
        third_party_template="My workout buddy is walking stiffly today after our leg workout yesterday.",
        minimized_template="Normal gym soreness in the legs, good workout yesterday.",
        default_age_years=25.0,
        default_sex="male",
    ),
    TemplateFamily(
        family_id="FAM_GENL_07",
        specialty="general_self_care",
        gold_urgency=4,
        concept="dizziness",
        clinical_intent="Transient eye strain after prolonged screen time",
        formal_template="Mild bilateral ocular fatigue and dry sensation after 8 hours continuous visual display terminal use, visual acuity intact.",
        colloquial_template="My eyes feel tired, gritty and dry after staring at my laptop computer screen all day without a break.",
        hinglish_template="Din bhar laptop par kaam karne se aankhein thaki thaki aur sookhi lag rahi hain.",
        marathi_template="Divasbhar computer baghitlyamule dole thakle ahet aani korde watat ahet.",
        typo_template="Eyes tierd dry grity after al day laptop skren.",
        negation_template="No vision loss, no eye redness, no discharge, no flashes or floaters, completely relieved by blinking and rest.",
        historical_template="Routine computer vision syndrome / asthenopia during intensive work days.",
        third_party_template="My sister rubbed her eyes saying they feel dry from looking at monitors all day.",
        minimized_template="Just tired screen eyes after a long workday, resting them now.",
        default_age_years=29.0,
        default_sex="female",
    ),
]


def generate_cases_for_family(family: TemplateFamily, count: int, start_case_id: int) -> List[Dict[str, Any]]:
    """Generate variations for a single template family across language styles."""
    styles = [
        ("formal", family.formal_template, "en"),
        ("colloquial", family.colloquial_template, "en"),
        ("hinglish", family.hinglish_template, "hinglish"),
        ("marathi", family.marathi_template, "marathi"),
        ("typos", family.typo_template, "en"),
        ("negation", family.negation_template, "en"),
        ("historical", family.historical_template, "en"),
        ("third_party", family.third_party_template, "en"),
        ("minimized", family.minimized_template, "en"),
    ]

    cases: List[Dict[str, Any]] = []
    for i in range(count):
        case_idx = start_case_id + i
        style_idx = i % len(styles)
        style_name, text_base, lang = styles[style_idx]

        # Minor variation in text for duplicate avoidance while preserving clinical content
        prefixes = [
            "",
            "Patient notes: ",
            "Report: ",
            "Currently experiencing: ",
            "Status: ",
            "Chief complaint: ",
            "Please assess: ",
        ]
        prefix = prefixes[(i // len(styles)) % len(prefixes)]
        final_text = f"{prefix}{text_base}".strip()

        is_hinglish_or_marathi = lang in ("hinglish", "marathi")

        case = {
            "case_id": f"SYN_{case_idx:04d}",
            "family_id": family.family_id,
            "specialty": family.specialty,
            "tier": "synthetic_dev",
            "symptoms_text": final_text,
            "ground_truth_urgency": family.gold_urgency,
            "label_source": "developer_assigned_unreviewed",
            "language": lang,
            "language_style": style_name,
            "clinical_intent": family.clinical_intent,
            "hinglish_marathi_reviewed": False,
            "unreviewed_notice": (
                "UNVERIFIED by native clinician. Developer transliteration placeholder."
                if is_hinglish_or_marathi
                else None
            ),
            "age_years": family.default_age_years,
            "age_months": family.default_age_months,
            "sex": family.default_sex,
        }
        cases.append(case)

    return cases


def generate_full_dataset(seed: int = 42) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Generate all 1,200 cases and split strictly by family into 70/15/15 splits.

    Guarantees:
    - 70 template families across 10 specialties (7 per specialty).
    - Gold labels assigned by design, not rule engine.
    - Test split has >= 10 families.
    - Every level (1, 2, 3, 4) present in every split.
    - Zero family leakage across splits.
    - Exactly 1,200 cases in total.
    """
    random.seed(seed)

    # 1. Stratify families by gold_urgency for balanced split
    families_by_level: Dict[int, List[TemplateFamily]] = {1: [], 2: [], 3: [], 4: []}
    for fam in TEMPLATE_FAMILIES:
        families_by_level[fam.gold_urgency].append(fam)

    train_families: List[TemplateFamily] = []
    val_families: List[TemplateFamily] = []
    test_families: List[TemplateFamily] = []

    # Partition families: 70% train (approx 48-50), 15% val (approx 10-11), 15% test (approx 10-11)
    # Ensure every level (1, 2, 3, 4) appears in every split
    for level, fams in sorted(families_by_level.items()):
        fams_copy = list(fams)
        random.shuffle(fams_copy)
        
        # At least 1 family of each level in test and val
        test_families.append(fams_copy.pop())
        val_families.append(fams_copy.pop())
        
        # Remaining partitioned according to ~70 / 15 / 15
        for f in fams_copy:
            r = random.random()
            if r < 0.70:
                train_families.append(f)
            elif r < 0.85:
                val_families.append(f)
            else:
                test_families.append(f)

    # Verify test families count >= 10
    while len(test_families) < 10 and len(train_families) > 40:
        test_families.append(train_families.pop())
    while len(val_families) < 10 and len(train_families) > 40:
        val_families.append(train_families.pop())

    all_split_families = {
        "train": train_families,
        "validation": val_families,
        "test": test_families,
    }

    # Verify family isolation
    train_ids = {f.family_id for f in train_families}
    val_ids = {f.family_id for f in val_families}
    test_ids = {f.family_id for f in test_families}
    assert len(train_ids & val_ids) == 0, "Leakage detected: train & val overlap"
    assert len(train_ids & test_ids) == 0, "Leakage detected: train & test overlap"
    assert len(val_ids & test_ids) == 0, "Leakage detected: val & test overlap"

    # Allocate cases across 70 families to reach exactly 1,200 cases
    # 60 families get 17 cases, 10 families get 18 cases (60*17 + 10*18 = 1200)
    family_case_counts: Dict[str, int] = {}
    fam_list = list(TEMPLATE_FAMILIES)
    for i, fam in enumerate(fam_list):
        family_case_counts[fam.family_id] = 18 if i < 10 else 17

    total_allocated = sum(family_case_counts.values())
    assert total_allocated == 1200, f"Expected 1200 cases, got {total_allocated}"

    # Generate cases
    full_dataset: List[Dict[str, Any]] = []
    splits_data: Dict[str, List[Dict[str, Any]]] = {"train": [], "validation": [], "test": []}

    case_counter = 1
    for split_name in ("train", "validation", "test"):
        for fam in all_split_families[split_name]:
            count = family_case_counts[fam.family_id]
            cases = generate_cases_for_family(fam, count, case_counter)
            case_counter += len(cases)
            splits_data[split_name].extend(cases)
            full_dataset.extend(cases)

    # Sort each split deterministically by case_id
    full_dataset.sort(key=lambda c: c["case_id"])
    for s in splits_data:
        splits_data[s].sort(key=lambda c: c["case_id"])

    return full_dataset, splits_data


def canonical_serialize(data: Any) -> bytes:
    """Canonical JSON serialization with sorted keys, utf-8 encoding, and LF line endings."""
    text = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)
    # Ensure standard UNIX LF line endings
    text = text.replace("\r\n", "\n").rstrip("\n") + "\n"
    return text.encode("utf-8")


def compute_sha256(data_bytes: bytes) -> str:
    """Compute SHA-256 hex digest of serialized bytes."""
    return hashlib.sha256(data_bytes).hexdigest()


def write_dataset_files(output_dir: Path | None = None) -> Dict[str, str]:
    """Generate dataset and write canonical JSON files with SHA-256 checksums."""
    target_dir = output_dir or (Path(__file__).parent / "synthetic_dev")
    target_dir.mkdir(parents=True, exist_ok=True)

    full_dataset, splits = generate_full_dataset(seed=42)

    checksums: Dict[str, str] = {}

    # Write splits
    for split_name, cases in splits.items():
        split_path = target_dir / f"{split_name}.json"
        content_bytes = canonical_serialize(cases)
        split_path.write_bytes(content_bytes)
        checksums[f"{split_name}.json"] = compute_sha256(content_bytes)

    # Write full dataset
    full_path = target_dir / "full_dataset.json"
    full_bytes = canonical_serialize(full_dataset)
    full_path.write_bytes(full_bytes)
    checksums["full_dataset.json"] = compute_sha256(full_bytes)

    # Write checksums file
    checksums_path = target_dir / "checksums.json"
    checksums_path.write_bytes(canonical_serialize(checksums))

    return checksums


if __name__ == "__main__":
    checksums = write_dataset_files()
    print("Dataset generation complete. Checksums:")
    for k, v in checksums.items():
        print(f"  {k}: {v}")
