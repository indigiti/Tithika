<?php
declare(strict_types=1);

function tk_kumbh_pages(): array {
    return [
        'calendar' => ['स्नान दिनदर्शिका','अमृत स्नान आणि पर्वकाळ: नाशिक व त्र्यंबकेश्वरची अधिकृत दिनांकसूची.'],
        'nashik' => ['नाशिक यात्रा मार्गदर्शक','रामतीर्थ, पंचवटी, नाशिक रोड आणि स्नानदिवसाच्या अधिकृत प्रवास सूचनांचा मार्गदर्शक.'],
        'trimbakeshwar' => ['त्र्यंबकेश्वर यात्रा मार्गदर्शक','कुशावर्त तीर्थ, ज्योतिर्लिंग, ब्रह्मगिरी आणि स्वतंत्र स्नान दिनदर्शिकेसह यात्रा मार्गदर्शक.'],
        'faq' => ['कुंभ ज्ञानकोश','कुंभाचा इतिहास, विधी, आखाडे, यात्रा नियोजन आणि पर्यावरण यांवरील ७२ मराठी प्रश्नोत्तरे.'],
        'scriptures' => ['ग्रंथसंदर्भ','शिवपुराण, गौतमीमाहात्म्य, रामायण आणि इतर सोळा ग्रंथ व परंपरा संदर्भांचे मराठी स्पष्टीकरण.'],
        'history' => ['इतिहास व पुरावे','सिंहस्थाच्या दस्तऐवजी नोंदी, धार्मिक परंपरा आणि सामाजिक संशोधन यांचा स्वतंत्र मागोवा.'],
        'help' => ['सूचना व मदत','अधिकृत प्रवास सूचना, आपत्कालीन संपर्क, हरवलेल्या व्यक्तीसाठी मदत आणि सुलभतेची माहिती.'],
        'media' => ['कथा व माध्यमे','अधिकृत कार्यक्रम आणि प्रसारण दुवे; ऐतिहासिक छायाचित्रे वापरण्याची संपादकीय धोरणे.'],
        'english' => ['Simhastha visitor essentials','An English introduction to Simhastha with key bathing dates, separate venue information and official links.'],
    ];
}
function tk_kumbh_key(string $slug): ?string {
    $root = 'festivals/mahakumbh';
    if ($slug === $root) return '';
    if (!str_starts_with($slug, $root.'/')) return null;
    $key = substr($slug, strlen($root)+1);
    return isset(tk_kumbh_pages()[$key]) ? $key : null;
}
function tk_kumbh_data(): array {
    static $data;
    return $data ??= require dirname(__DIR__).'/config/mahakumbh.php';
}
function tk_kumbh_records(string $name): array {
    if (!in_array($name, ['faq','scriptures'], true)) return [];
    return json_decode((string)file_get_contents(dirname(__DIR__).'/config/mahakumbh-'.$name.'.json'), true, 512, JSON_THROW_ON_ERROR);
}
function tk_kumbh_e(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function tk_kumbh_url(string $suffix = ''): string {
    return tithika_pretty_url('festivals/mahakumbh'.($suffix === '' ? '' : '/'.$suffix));
}
function tk_kumbh_link(string $key, string $label = '', string $fragment = ''): void {
    echo '<a href="'.tk_kumbh_e(tk_kumbh_url($key).$fragment).'">'.tk_kumbh_e($label ?: (tk_kumbh_pages()[$key][0] ?? 'सिंहस्थ महाकुंभ')).'</a>';
}
function tk_kumbh_source(string $path, string $label): void {
    $url = str_starts_with($path,'https://') ? $path : tk_kumbh_data()['source'].$path;
    echo '<a href="'.tk_kumbh_e($url).'">'.tk_kumbh_e($label).'</a>';
}
function tk_kumbh_next(string $today): ?array {
    foreach (tk_kumbh_data()['events'] as $event) {
        if ($event[0] >= $today && str_starts_with($event[1], 'amrut-')) return $event;
    }
    return null;
}
function tk_kumbh_notices(string $now): array {
    return array_values(array_filter(tk_kumbh_data()['notices'], static function(array $n) use ($now): bool {
        return ($n['status'] ?? '') === 'verified'
            && !empty($n['authority']) && !empty($n['reviewed_by'])
            && str_starts_with($n['url'] ?? '', 'https://')
            && !empty($n['from']) && !empty($n['until'])
            && $n['from'] <= $now && $n['until'] > $now;
    }));
}
function tk_kumbh_place(string $venue): string {
    return ['nashik'=>'नाशिक','trimbakeshwar'=>'त्र्यंबकेश्वर','edition'=>'सिंहस्थ आवृत्ती'][$venue] ?? '';
}
function tk_kumbh_calendar(string $today): void {
    $data = tk_kumbh_data();
    $venue = $_GET['venue'] ?? 'all';
    if (!in_array($venue, ['all','nashik','trimbakeshwar'], true)) $venue = 'all';
    $eventId = $_GET['event'] ?? '';
    $rows = $data['events'];
    foreach ($data['parvakal'] as $place=>$dates) {
        foreach (explode(' ', $dates) as $date) $rows[] = [$date,'parva-'.$place.'-'.$date,$place,'पर्वकाळ',null];
    }
    usort($rows, static fn(array $a,array $b): int => $a[0] <=> $b[0]);
    $single = null;
    foreach ($rows as $row) if ($row[1] === $eventId) $single = $row;
    ?>
    <p>प्रमुख स्नान, इतर कार्यक्रम आणि केंद्रनिहाय पर्वकाळ. सार्वजनिक प्रवेशवेळ वेगळी असू शकते.</p>
    <p><?php tk_kumbh_source('snan-calendar','महाराष्ट्र प्राधिकरणाची दिनदर्शिका'); ?> · <?php tk_kumbh_source('live-event-schedule','अद्ययावत कार्यक्रम'); ?> · स्रोत तपासला: <?= tk_kumbh_e($data['source_checked']) ?></p>
    <?php if ($single): ?>
        <section class="tk-kumbh-card">
            <h2><?= tk_kumbh_e($single[3]) ?></h2>
            <p><time datetime="<?= tk_kumbh_e($single[0]) ?>"><?= tk_kumbh_e($single[0]) ?></time> · <?= tk_kumbh_e(tk_kumbh_place($single[2])) ?> · <?= $single[0] < $today ? 'मागील दिनांक' : 'अधिसूचित दिनांक' ?></p>
            <p><?= $single[4] ? 'कार्यक्रम वेळ (IST): '.tk_kumbh_e($single[4]) : 'सार्वजनिक प्रवेशवेळ या नोंदीत दिलेली नाही.' ?></p>
            <?php if ($single[2] !== 'edition') tk_kumbh_link($single[2]); ?>
            <p><?php tk_kumbh_link('calendar','संपूर्ण दिनदर्शिका'); ?></p>
        </section>
    <?php else: ?>
        <form method="get" action="<?= tk_kumbh_e(tk_kumbh_url('calendar')) ?>" class="tk-kumbh-tools">
            <label for="tk-kumbh-venue">केंद्र निवडा</label>
            <select id="tk-kumbh-venue" name="venue">
                <?php foreach (['all'=>'सर्व','nashik'=>'नाशिक','trimbakeshwar'=>'त्र्यंबकेश्वर'] as $key=>$label): ?>
                    <option value="<?= tk_kumbh_e($key) ?>"<?= $key === $venue ? ' selected' : '' ?>><?= tk_kumbh_e($label) ?></option>
                <?php endforeach; ?>
            </select><button type="submit">दाखवा</button>
        </form>
        <?php foreach (['प्रमुख अमृत स्नान व कार्यक्रम','केंद्रनिहाय पर्वकाळ'] as $i=>$title): ?>
            <h2><?= tk_kumbh_e($title) ?></h2>
            <ul class="tk-kumbh-dates">
                <?php foreach ($rows as [$date,$id,$place,$name,$time]):
                    if (str_starts_with($id,'parva-') !== (bool)$i || ($venue !== 'all' && $venue !== $place && $place !== 'edition')) continue; ?>
                    <li><time datetime="<?= tk_kumbh_e($date) ?>"><?= tk_kumbh_e($date) ?></time>
                        <a href="<?= tk_kumbh_e(tk_kumbh_url('calendar').'?event='.rawurlencode($id)) ?>"><?= tk_kumbh_e($name) ?></a>
                        <span><?= tk_kumbh_e(tk_kumbh_place($place)) ?><?= $date < $today ? ' · मागील' : '' ?></span>
                    </li>
                <?php endforeach; ?>
            </ul>
        <?php endforeach; ?>
    <?php endif;
}
function tk_kumbh_render(string $key): void {
    $now = new DateTimeImmutable('now', new DateTimeZone('Asia/Kolkata'));
    $today = $now->format('Y-m-d');
    $notices = tk_kumbh_notices($now->format('Y-m-d\TH:i:s'));
    ?>
    <div class="tk-kumbh" lang="<?= $key === 'english' ? 'en' : 'mr' ?>">
    <?php if ($key !== 'english'): ?>
        <p class="tk-kumbh-disclosure">Tithika · स्वतंत्र माहिती मार्गदर्शक. हे शासकीय संकेतस्थळ नाही.</p>
        <nav class="tk-kumbh-nav" aria-label="सिंहस्थ विभाग">
            <?php tk_kumbh_link('','कुंभक्षेत्रे'); foreach (tk_kumbh_pages() as $k=>$p) tk_kumbh_link($k,$k === 'english' ? 'English essentials' : $p[0]); ?>
        </nav>
    <?php endif; ?>
    <?php if ($key === '' || $key === 'help'): foreach ($notices as $n): ?>
        <aside class="tk-kumbh-card"><strong><?= tk_kumbh_e($n['authority']) ?></strong> · <?= tk_kumbh_e($n['title']) ?> · <?php tk_kumbh_source($n['url'],'मूळ सूचना'); ?></aside>
    <?php endforeach; endif; ?>
    <?php if ($key !== ''): ?><h1><?= tk_kumbh_e(tk_kumbh_pages()[$key][0]) ?></h1><?php endif; ?>
    <?php if ($key === ''): ?>
        <section class="tk-kumbh-hero">
            <p>नाशिक–त्र्यंबकेश्वर · २०२७</p>
            <h1>सिंहस्थ महाकुंभ</h1>
            <p>स्नानाचा दिवस, योग्य तीर्थक्षेत्र आणि अधिकृत सूचना. पुढे गोदावरीच्या परंपरेचा आणि चारही कुंभक्षेत्रांचा परिचय.</p>
            <div class="tk-kumbh-nav"><?php tk_kumbh_link('calendar'); tk_kumbh_link('nashik','यात्रेचे नियोजन'); tk_kumbh_link('help'); ?></div>
        </section>
        <?php if ($next = tk_kumbh_next($today)): ?>
            <section class="tk-kumbh-card"><h2>पुढील प्रमुख अमृत स्नान</h2>
              <p><time datetime="<?= tk_kumbh_e($next[0]) ?>"><?= tk_kumbh_e($next[0]) ?></time> · <?= tk_kumbh_e($next[3].' · '.tk_kumbh_place($next[2])) ?></p>
              <p><?php tk_kumbh_link('calendar','संपूर्ण दिनदर्शिका'); ?> · <?php tk_kumbh_source('snan-calendar','अधिकृत स्रोत'); ?></p>
            </section>
        <?php else: ?><p><?php tk_kumbh_link('calendar','या आवृत्तीचे संग्रहित कार्यक्रम'); ?></p><?php endif; ?>
        <h2>स्नान केंद्र निवडा</h2>
        <div class="tk-kumbh-grid">
            <section class="tk-kumbh-card"><h3>नाशिक</h3><p>रामतीर्थ व पंचवटी. स्नान आणि प्रवासासाठी नाशिकच्या सूचना वेगळ्या तपासा.</p><?php tk_kumbh_link('nashik'); ?></section>
            <section class="tk-kumbh-card"><h3>त्र्यंबकेश्वर</h3><p>कुशावर्त तीर्थ, त्र्यंबकेश्वर ज्योतिर्लिंग व ब्रह्मगिरी. प्रवेश सूचना स्वतंत्र आहेत.</p><?php tk_kumbh_link('trimbakeshwar'); ?></section>
        </div>
        <h2>भारतातील चार कुंभक्षेत्रे</h2>
        <div class="tk-kumbh-nav"><?php foreach (['prayagraj'=>'प्रयागराज','haridwar'=>'हरिद्वार','ujjain'=>'उज्जैन','nashik-trimbakeshwar'=>'नाशिक–त्र्यंबकेश्वर'] as $k=>$label) tk_kumbh_link($k,$label); ?></div>
        <h2>कुंभाचा अभ्यास</h2>
        <div class="tk-kumbh-nav"><?php tk_kumbh_link('faq'); tk_kumbh_link('scriptures','सिंहस्थ का म्हणतात?','#simhastha'); tk_kumbh_link('history'); ?></div>
    <?php elseif ($key === 'calendar'): tk_kumbh_calendar($today); ?>
    <?php elseif ($key === 'nashik' || $key === 'trimbakeshwar'): $nashik = $key === 'nashik'; ?>
        <p><?= $nashik ? 'रामतीर्थ हे नाशिकच्या अधिकृत स्नान दिनदर्शिकेतील स्थळ आहे. पंचवटीचा रामायणाशी संबंध स्वतंत्रपणे वाचा.' : 'कुशावर्त तीर्थ हे त्र्यंबकेश्वरच्या अधिकृत स्नान दिनदर्शिकेतील स्थळ. ज्योतिर्लिंग आणि ब्रह्मगिरी ही स्वतंत्र दर्शनस्थळे आहेत.' ?></p>
        <h2>कसे पोहोचाल</h2>
        <p><?= $nashik ? 'रेल्वे प्रवासासाठी नाशिक रोडचा पर्याय पहा. रेल्वे स्थानक ते घाट यासाठी त्या दिवसाचे शहरातील मार्ग व वाहन निर्बंध तपासा.' : 'बहुतेक प्रवासांसाठी नाशिक हा प्रवेशबिंदू आहे. तेथून त्र्यंबकेश्वरचा पुढील रस्ता प्रवास आणि परतीची व्यवस्था आधी ठरवा.' ?></p>
        <p><?php tk_kumbh_source('how-to-reach','अधिकृत रेल्वे, रस्ता व विमान मार्गदर्शक'); ?></p>
        <h2>प्रवेश, सुविधा व सुलभता</h2>
        <p>पार्किंग, शटल, सार्वजनिक स्नान गेट, वैद्यकीय मदत, पिण्याचे पाणी, शौचालये आणि सुलभ मार्ग यासाठी प्रवासाच्या दिवशी अधिकृत सूचना तपासा. या पानावर अप्रमाणित व्यवस्था दिलेल्या नाहीत.</p>
        <p>ब्राउझरच्या Print पर्यायाने हा मजकूर छापा; छापील प्रत वापरण्यापूर्वी सूचना पुन्हा तपासा.</p>
        <div class="tk-kumbh-nav"><?php tk_kumbh_link('calendar','केंद्राची दिनदर्शिका','?venue='.$key); tk_kumbh_link('help'); tk_kumbh_link('scriptures',$nashik ? 'पंचवटीचा ग्रंथसंदर्भ' : 'कुशावर्ताचा ग्रंथसंदर्भ',$nashik ? '#panchavati' : '#kushavarta'); ?></div>
    <?php elseif ($key === 'faq'):
        $raw = $_GET['q'] ?? '';
        $q = is_string($raw) ? mb_substr(trim($raw),0,100) : '';
        if (in_array(mb_strtolower($q), ['kushavarta','kushawarta','kushavart'], true)) $q = 'कुशावर्त';
        ?>
        <form method="get" action="<?= tk_kumbh_e(tk_kumbh_url('faq')) ?>" class="tk-kumbh-tools">
            <label for="tk-kumbh-q">प्रश्न शोधा</label><input type="search" id="tk-kumbh-q" name="q" value="<?= tk_kumbh_e($q) ?>" maxlength="100" placeholder="उदा. कुशावर्त किंवा Kushavarta">
            <button type="submit">शोधा</button><?php tk_kumbh_link('faq','सर्व प्रश्न'); ?>
        </form>
        <?php $count = 0; foreach (tk_kumbh_records('faq') as $group):
            $matched = array_filter($group['questions'], static fn(array $item): bool => $q === '' || mb_stripos($group['title'].' '.$item['q'].' '.$item['a'],$q) !== false);
            if (!$matched) continue; $count += count($matched); ?>
            <section><h2><?= tk_kumbh_e($group['title']) ?></h2>
            <?php foreach ($matched as $item): ?>
                <article class="tk-kumbh-card" id="q-<?= (int)$item['id'] ?>">
                    <h3><a href="#q-<?= (int)$item['id'] ?>"><?= tk_kumbh_e($item['q']) ?></a></h3><p><?= tk_kumbh_e($item['a']) ?></p>
                </article>
            <?php endforeach; ?>
            <p><?php tk_kumbh_source($group['source'],'विषयाचा संदर्भ'); ?></p></section>
        <?php endforeach; if (!$count): ?><p>या शोधाशी जुळणारा प्रश्न सापडला नाही.</p><?php endif; ?>
        <p><?php tk_kumbh_link('scriptures'); ?> · <?php tk_kumbh_link('history'); ?> · <?php tk_kumbh_link('calendar'); ?></p>
    <?php elseif ($key === 'scriptures'): ?>
        <p>गौतमीमाहात्म्याचे अध्यायक्रमांक स्वतंत्र आवृत्तीचे आहेत. इतर आवृत्त्यांत क्रम बदलू शकतो. ग्रंथातील धार्मिक फलश्रुती हा ऐतिहासिक किंवा वैद्यकीय पुरावा नाही.</p>
        <?php foreach (tk_kumbh_records('scriptures') as $card): ?>
            <section class="tk-kumbh-card" id="<?= tk_kumbh_e($card['id']) ?>">
                <p><small><?= tk_kumbh_e($card['label']) ?></small></p>
                <h2><a href="#<?= tk_kumbh_e($card['id']) ?>"><?= tk_kumbh_e($card['title']) ?></a></h2>
                <?php if ($card['original']): ?>
                    <p lang="sa"><?= nl2br(tk_kumbh_e($card['original'])) ?></p><p><?php tk_kumbh_source($card['originalSource'],'मूळ संस्कृत पाठ'); ?></p>
                <?php endif; ?>
                <p><strong>शब्दार्थ:</strong> <?= tk_kumbh_e($card['gloss']) ?></p>
                <p><strong>मराठी भावार्थ:</strong> <?= tk_kumbh_e($card['meaning']) ?></p>
                <p><?php tk_kumbh_source($card['source'],'उतारा व वापरलेली आवृत्ती'); ?></p>
            </section>
        <?php endforeach; ?>
    <?php elseif ($key === 'history'): ?>
        <h2>तीर्थपरंपरा आणि ऐतिहासिक नोंदी</h2>
        <p>पुराणांतील गोदावरीचे माहात्म्य धार्मिक परंपरा स्पष्ट करते; ते मेळ्याचे स्थापना वर्ष ठरवत नाही.</p>
        <section class="tk-kumbh-card"><h3>पेशवाई · १७८९ चा संदर्भ</h3><p>प्राधिकरणाच्या ऐतिहासिक सारांशात स्नानक्रमाशी संबंधित वादाची नोंद दिली आहे. मूळ आदेश स्वतंत्रपणे पडताळणे बाकी आहे.</p><?php tk_kumbh_source('historical-timeline-of-the-nashik-kumbh','प्राधिकरणाचा ऐतिहासिक सारांश'); ?></section>
        <section class="tk-kumbh-card"><h3>नाशिक जिल्हा गॅझेटियर · त्र्यंबक</h3><p>कुशावर्त आणि सिंहस्थ यात्रेचे वर्णन. गॅझेटियरमध्ये नोंदवलेल्या आख्यायिका आणि दस्तऐवजी निरीक्षणे एकच नाहीत.</p><?php tk_kumbh_source('https://gazetteers.maharashtra.gov.in/cultural.maharashtra.gov.in/english/gazetteer/Nasik/022%20Places/001%20Place.htm','जिल्हा गॅझेटियर'); ?></section>
        <section class="tk-kumbh-card"><h3>१९२० · संग्रह संदर्भ, प्रत पडताळणी बाकी</h3><p>६ मे १९२०, पृ. ११५६, नोटीस १३८० हा शोधासाठी संदर्भ आहे. मूळ प्रत पडताळल्याशिवाय लिप्यंतरण किंवा स्थापनेचा दावा प्रसिद्ध केलेला नाही.</p></section>
        <section class="tk-kumbh-card"><h3>२०१७ · अमूर्त सांस्कृतिक वारसा</h3><p>युनेस्कोने कुंभमेळ्याच्या जिवंत परंपरेची नोंद केली. ही नेमक्या स्थापना वर्षाची पडताळणी नाही.</p><?php tk_kumbh_source('https://ich.unesco.org/en/RL/kumbh-mela-01258','UNESCO नोंद'); ?></section>
        <h2>आध्यात्मिक महत्त्व आणि सामाजिक संशोधन</h2><p>स्नान, दर्शन, दान व सेवा यांना धार्मिक अर्थ आहे. २०११ माघ मेळ्यातील एका अभ्यासात सहभागींच्या स्वतः नोंदवलेल्या कल्याणात सुधारणा आढळली. यावरून नाशिकमधील स्नानाचे वैद्यकीय लाभ सिद्ध होत नाहीत.</p>
        <p><?php tk_kumbh_source('https://pmc.ncbi.nlm.nih.gov/articles/PMC3474838/','मूळ संशोधन'); ?> · <?php tk_kumbh_link('scriptures'); ?></p>
    <?php elseif ($key === 'help'): ?>
        <h2>तातडीची मदत</h2><p>भारताची एकत्रित आपत्कालीन सेवा: <a href="tel:112">११२ वर कॉल करा</a>.</p>
        <p><?php tk_kumbh_source('emergency-contacts','स्थानिक आपत्कालीन संपर्क'); ?> · <?php tk_kumbh_source('https://www.mha.gov.in/emergency-response-support-system-erss','११२ चा अधिकृत स्रोत'); ?></p>
        <h2>प्रवेश सूचना व सुविधा</h2><p>निघण्यापूर्वी आणि पोहोचल्यावर घाट, प्रवेशद्वार, वाहन निर्बंध, वैद्यकीय केंद्र, पाणी आणि सुलभ शौचालयांची अधिकृत माहिती तपासा.</p>
        <p><?php tk_kumbh_source('','प्राधिकरण: सूचना व सुविधा'); ?> · <?php tk_kumbh_source('safety-guidelines','सुरक्षा मार्गदर्शक'); ?></p>
        <h2>गटापासून वेगळे झाल्यास</h2><p>अधिकृत मदत कक्ष किंवा पोलिसांना जवळचे ठिकाण आणि शेवटचे भेटस्थान सांगा. सार्वजनिक पोस्टमध्ये ओळखपत्र किंवा वैयक्तिक तपशील टाकू नका.</p>
        <h2>दुरुस्ती कळवा</h2><p>पानाची लिंक, संबंधित मजकूर आणि पडताळता येणारा स्रोत द्या. <a href="<?= tk_kumbh_e(tithika_pretty_url('learn/contact')) ?>">Tithika संपर्क पान</a>.</p>
    <?php elseif ($key === 'media'): ?>
        <h2>अधिकृत कार्यक्रम व प्रसारण</h2><p>प्रक्षेपणाच्या सूचना आयोजकाकडून पडताळा. या पानावर थेट प्रसारण चालू असल्याचा दावा नाही.</p>
        <p><?php tk_kumbh_source('live-event-schedule','अधिकृत कार्यक्रम व प्रसारण सूचना'); ?></p>
        <h2>छायाचित्रे व संग्रह</h2><p>स्रोत, वर्ष, ठिकाण आणि वापर हक्क पडताळल्यानंतरच छायाचित्रे किंवा चित्रफिती जोडल्या जातील.</p><p><?php tk_kumbh_link('history'); ?></p>
    <?php elseif ($key === 'english'): ?>
        <p>Tithika is an independent guide, not the event authority. <?php tk_kumbh_link('','मराठी मुख्यपृष्ठ'); ?></p>
        <h2>2027 major bathing dates</h2>
        <p>The authority lists 2 August, 31 August and 11 September in Nashik, and 12 September at Kushavarta Tirth, Trimbakeshwar. The third observance is split across the two centres. Verify public-access hours before travelling.</p>
        <p><?php tk_kumbh_source('snan-calendar','Official English calendar'); ?> · <?php tk_kumbh_source('how-to-reach','Official travel guide'); ?> · <?php tk_kumbh_source('emergency-contacts','Official contacts'); ?></p>
        <h2>Choose the right centre</h2><p>Nashik’s calendar names Ramtirth. Trimbakeshwar’s calendar names Kushavarta Tirth. For detailed Marathi guidance, use the links below.</p>
        <p><?php tk_kumbh_link('nashik','Nashik guide (Marathi)'); ?> · <?php tk_kumbh_link('trimbakeshwar','Trimbakeshwar guide (Marathi)'); ?> · <?php tk_kumbh_link('calendar','Full venue-filtered calendar (Marathi)'); ?></p>
    <?php endif; ?>
    </div>
    <?php
}
