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
function tk_kumbh_date_label(string $iso, bool $monthOnly = false): string {
    $months = [1=>'जानेवारी','फेब्रुवारी','मार्च','एप्रिल','मे','जून','जुलै','ऑगस्ट','सप्टेंबर','ऑक्टोबर','नोव्हेंबर','डिसेंबर'];
    [$year,$month,$day] = array_map('intval', explode('-', $iso));
    $label = ($monthOnly ? '' : $day.' ').$months[$month].' '.$year;
    return strtr($label, ['0'=>'०','1'=>'१','2'=>'२','3'=>'३','4'=>'४','5'=>'५','6'=>'६','7'=>'७','8'=>'८','9'=>'९']);
}

function tk_kumbh_calendar(string $today): void {
    $data = tk_kumbh_data();
    $venue = $_GET['venue'] ?? 'all';
    if (!in_array($venue, ['all','nashik','trimbakeshwar'], true)) $venue = 'all';
    $eventId = is_string($_GET['event'] ?? null) ? $_GET['event'] : '';
    $rows = $data['events'];
    foreach ($data['parvakal'] as $place=>$dates) {
        foreach (explode(' ', $dates) as $date) $rows[] = [$date,'parva-'.$place.'-'.$date,$place,'पर्वकाळ',null];
    }
    usort($rows, static fn(array $a,array $b): int => $a[0] <=> $b[0]);
    $single = null;
    foreach ($rows as $row) if ($row[1] === $eventId) $single = $row;
    ?>
    <div class="tk-km-sourcebar">
        <div><strong>अधिकृत स्रोत</strong> · <span>तपासणी: <?= tk_kumbh_e(tk_kumbh_date_label($data['source_checked'])) ?></span></div>
        <div><?php tk_kumbh_source('snan-calendar','मूळ दिनदर्शिका'); ?> · <?php tk_kumbh_source('live-event-schedule','अद्ययावत कार्यक्रम'); ?></div>
    </div>
    <?php if ($single): ?>
        <section class="tk-km-event-detail">
            <p class="tk-km-eyebrow"><?= $single[0] < $today ? 'मागील दिनांक' : 'अधिसूचित दिनांक' ?></p>
            <h2><?= tk_kumbh_e($single[3]) ?></h2>
            <p><time datetime="<?= tk_kumbh_e($single[0]) ?>"><?= tk_kumbh_e(tk_kumbh_date_label($single[0])) ?></time> · <?= tk_kumbh_e(tk_kumbh_place($single[2])) ?></p>
            <p><?= $single[4] ? 'कार्यक्रम वेळ (IST): '.tk_kumbh_e($single[4]) : 'सार्वजनिक प्रवेशवेळ या नोंदीत दिलेली नाही.' ?></p>
            <?php if ($single[2] !== 'edition'): ?><p><?php tk_kumbh_link($single[2]); ?> · <?php tk_kumbh_link('calendar','या केंद्राची दिनदर्शिका','?venue='.$single[2]); ?></p><?php endif; ?>
            <p><?php tk_kumbh_link('calendar','← संपूर्ण दिनदर्शिका'); ?></p>
        </section>
    <?php else:
        $visible = array_filter($rows, static fn(array $row): bool => $venue === 'all' || $row[2] === $venue || $row[2] === 'edition');
        $main = $months = [];
        foreach ($visible as $row) {
            if (str_starts_with($row[1], 'parva-')) $months[substr($row[0], 0, 7)][] = $row;
            else $main[] = $row;
        }
        $next = null;
        foreach ($main as $row) if ($row[0] >= $today && str_starts_with($row[1], 'amrut-')) { $next = $row; break; }
        ?>
        <nav class="tk-km-filters" aria-label="स्नान केंद्रानुसार दिनदर्शिका">
            <strong>स्नान केंद्र</strong>
            <?php foreach (['all'=>'सर्व केंद्रे','nashik'=>'नाशिक','trimbakeshwar'=>'त्र्यंबकेश्वर'] as $key=>$label): ?>
                <a href="<?= tk_kumbh_e(tk_kumbh_url('calendar').($key === 'all' ? '' : '?venue='.$key)) ?>"<?= $key === $venue ? ' aria-current="true"' : '' ?>><?= tk_kumbh_e($label) ?></a>
            <?php endforeach; ?>
        </nav>
        <?php if ($eventId !== ''): ?><p>हा कार्यक्रम सापडला नाही. संपूर्ण दिनदर्शिका खाली दिली आहे.</p><?php endif; ?>
        <?php if ($next): ?>
            <section class="tk-km-event-detail"><p class="tk-km-eyebrow">पुढील प्रमुख अमृत स्नान</p><h2><time datetime="<?= tk_kumbh_e($next[0]) ?>"><?= tk_kumbh_e(tk_kumbh_date_label($next[0])) ?></time></h2>
                <p><?= tk_kumbh_e($next[3].' · '.tk_kumbh_place($next[2])) ?> · <?php tk_kumbh_link('calendar','स्नानाचा तपशील →','?event='.rawurlencode($next[1])); ?></p>
            </section>
        <?php endif; ?>
        <h2>प्रमुख अमृत स्नान व कार्यक्रम</h2>
        <?php tk_kumbh_date_rows($main, $today); ?>
        <h2 id="parvakal">केंद्रनिहाय पर्वकाळ</h2>
        <p>त्या महिन्यातील पर्वकाळ पाहण्यासाठी महिना उघडा.</p>
        <?php
        $openMonth = array_key_first($months);
        foreach ($months as $month=>$entries) {
            if ($entries[count($entries)-1][0] >= $today) { $openMonth = $month; break; }
        }
        foreach ($months as $month=>$entries): ?>
            <details class="tk-km-disclosure"<?= $month === $openMonth ? ' open' : '' ?>>
                <summary><?= tk_kumbh_e(tk_kumbh_date_label($month.'-01', true)) ?></summary>
                <?php tk_kumbh_date_rows($entries, $today); ?>
            </details>
        <?php endforeach; ?>
    <?php endif;
}

function tk_kumbh_date_rows(array $rows, string $today): void { ?>
    <ul class="tk-kumbh-dates tk-km-timeline" role="list">
    <?php foreach ($rows as [$date,$id,$place,$name,$time]): ?>
        <li<?= str_starts_with($id,'amrut-') ? ' class="tk-km-amrut"' : '' ?>>
            <time datetime="<?= tk_kumbh_e($date) ?>"><?= tk_kumbh_e(tk_kumbh_date_label($date)) ?></time>
            <a href="<?= tk_kumbh_e(tk_kumbh_url('calendar').'?event='.rawurlencode($id)) ?>"><?= tk_kumbh_e($name) ?></a>
            <span><?= tk_kumbh_e(tk_kumbh_place($place)) ?><?= $date < $today ? ' · मागील' : '' ?></span>
        </li>
    <?php endforeach; ?>
    </ul>
<?php }

function tk_kumbh_render(string $key): void {
    $now = new DateTimeImmutable('now', new DateTimeZone('Asia/Kolkata'));
    $today = $now->format('Y-m-d');
    $notices = tk_kumbh_notices($now->format('Y-m-d\TH:i:s'));
    ?>
    <div class="tk-kumbh<?= $key === '' ? ' tk-kumbh-portal' : ' tk-kumbh-inner' ?>" lang="<?= $key === 'english' ? 'en' : 'mr' ?>">
    <?php if ($key === ''): ?>
        <div class="tk-km-utility">
            <p>Tithika · स्वतंत्र माहिती मार्गदर्शक</p>
            <div><?php tk_kumbh_link('help','सूचना व मदत'); ?> <span aria-hidden="true">·</span> <?php tk_kumbh_link('english','English'); ?></div>
        </div>
    <?php elseif ($key !== 'english'): ?>
        <div class="tk-km-utility"><div><?php tk_kumbh_link('','← सिंहस्थ महाकुंभ'); ?></div><p>स्वतंत्र माहिती मार्गदर्शक · शासकीय संकेतस्थळ नाही</p></div>
        <nav class="tk-km-inner-nav" aria-label="सिंहस्थ विभाग">
            <?php foreach (['calendar'=>'दिनदर्शिका','nashik'=>'नाशिक','trimbakeshwar'=>'त्र्यंबकेश्वर','faq'=>'ज्ञानकोश','help'=>'मदत'] as $k=>$label): ?>
                <a href="<?= tk_kumbh_e(tk_kumbh_url($k)) ?>"<?= $k === $key ? ' aria-current="page"' : '' ?>><?= tk_kumbh_e($label) ?></a>
            <?php endforeach; ?>
            <details><summary>आणखी</summary><div><?php foreach (['scriptures','history','media','english'] as $k) tk_kumbh_link($k); ?></div></details>
        </nav>
    <?php endif; ?>
    <?php if ($key === '' || $key === 'help'): foreach ($notices as $n): ?>
        <aside class="tk-kumbh-card"><strong><?= tk_kumbh_e($n['authority']) ?></strong> · <?= tk_kumbh_e($n['title']) ?> · <?php tk_kumbh_source($n['url'],'मूळ सूचना'); ?></aside>
    <?php endforeach; endif; ?>
    <?php if ($key !== ''): ?><header class="tk-km-inner-title">
        <h1><?= tk_kumbh_e(tk_kumbh_pages()[$key][0]) ?></h1>
        <?php if ($key === 'calendar'): ?><p>अमृत स्नान, प्रमुख कार्यक्रम आणि केंद्रनिहाय पर्वकाळ. सार्वजनिक प्रवेशवेळ वेगळी असू शकते.</p><?php endif; ?>
        <?php if ($key === 'faq'): ?><p>७२ मराठी प्रश्नोत्तरे. विषय निवडा किंवा प्रश्न शोधा.</p><?php endif; ?>
    </header><?php endif; ?>
    <?php if ($key === ''): ?>
        <header class="tk-km-masthead">
            <p class="tk-km-eyebrow">◆ &nbsp; TITHIKA · यात्रा विशेष &nbsp; ◆</p>
            <h1>नाशिक–त्र्यंबकेश्वर<br><span>सिंहस्थ महाकुंभ २०२७</span></h1>
            <p>गोदावरीच्या तीरावरील श्रद्धा, परंपरा आणि यात्रेचा मराठी मार्गदर्शक.</p>
        </header>
        <div class="tk-km-gallery" aria-label="सिंहस्थ तीर्थक्षेत्रांची संग्रहित छायाचित्रे">
            <?php
            $photos = [
                ['trimbakeshwar', 'कुशावर्त · त्र्यंबकेश्वर', 'त्र्यंबकेश्वर येथील कुशावर्त तीर्थ', '8/87', 'Kushawart,_Trimbakeshwar_in_Maharashtra_state,_India.jpg', 'Prashant Kharote', '2014', 640],
                ['nashik', 'रामकुंड · नाशिक', 'संध्याकाळी रामकुंड परिसरातील गोदावरी नदी', '3/38', 'Ramkund_Nashik.jpg', 'Anup Moray', '2025', 1280],
                ['trimbakeshwar', 'त्र्यंबकेश्वर परिसर', 'त्र्यंबकेश्वर परिसरातील टेकडी आणि मंदिर', '8/82', 'Trimbakeshwar_temple.jpg', 'Chintuthakur9621', '2016', 960],
            ];
            foreach ($photos as $i=>[$route,$label,$alt,$hash,$file,$credit,$year,$size]):
                $name = rawurlencode($file);
                $src = "https://upload.wikimedia.org/wikipedia/commons/thumb/{$hash}/{$name}/{$size}px-{$name}";
            ?>
                <figure class="tk-km-photo">
                    <a href="<?= tk_kumbh_e(tk_kumbh_url($route)) ?>" aria-label="<?= tk_kumbh_e($label.' · यात्रा मार्गदर्शक') ?>">
                        <img src="<?= tk_kumbh_e($src) ?>" alt="<?= tk_kumbh_e($alt) ?>" width="960" height="720" decoding="async" referrerpolicy="no-referrer"<?= $i === 1 ? ' fetchpriority="high"' : ' loading="lazy"' ?>>
                        <span><?= tk_kumbh_e($label) ?></span>
                    </a>
                </figure>
            <?php endforeach; ?>
        </div>
        <div class="tk-km-event">
            <?php if ($next = tk_kumbh_next($today)):
                $date = new DateTimeImmutable($next[0], $now->getTimezone());
                $days = $now->setTime(0,0)->diff($date)->days;
                $months = [1=>'जानेवारी','फेब्रुवारी','मार्च','एप्रिल','मे','जून','जुलै','ऑगस्ट','सप्टेंबर','ऑक्टोबर','नोव्हेंबर','डिसेंबर'];
                $digits = ['०','१','२','३','४','५','६','७','८','९'];
                $marathi = static fn(string $value): string => str_replace(range(0,9),$digits,$value);
                ?>
                <div class="tk-km-date"><b><?= tk_kumbh_e($days ? $marathi((string)$days) : 'आज') ?></b><?php if ($days): ?><small>दिवस बाकी</small><?php endif; ?></div>
                <div class="tk-km-event-copy"><p class="tk-km-eyebrow">पुढील प्रमुख अमृत स्नान</p><h2><time datetime="<?= tk_kumbh_e($next[0]) ?>"><?= tk_kumbh_e($marathi($date->format('j')).' '.$months[(int)$date->format('n')].' '.$marathi($date->format('Y'))) ?></time></h2><p><?= tk_kumbh_e($next[3].' · '.tk_kumbh_place($next[2])) ?> · <?php tk_kumbh_source('snan-calendar','अधिकृत स्रोत'); ?></p></div>
                <?php tk_kumbh_link('calendar','स्नानाचा तपशील →','?event='.rawurlencode($next[1])); ?>
            <?php else: ?>
                <div class="tk-km-event-copy"><h2>सिंहस्थ दिनदर्शिका</h2><p>या आवृत्तीचे कार्यक्रम आणि पर्वकाळ पहा.</p></div>
                <?php tk_kumbh_link('calendar','दिनदर्शिका पहा →'); ?>
            <?php endif; ?>
        </div>
        <nav class="tk-km-shortcuts" aria-label="यात्रेचे जलद दुवे">
            <div><strong>तुम्हाला काय शोधायचे आहे?</strong><small>यात्रेची तयारी इथून सुरू करा</small></div>
            <?php foreach ([
                ['calendar','◷','स्नान दिनदर्शिका',''],
                ['','⌖','यात्रेचे नियोजन','#choose-venue'],
                ['help','✚','सूचना व मदत',''],
                ['faq','?','कुंभ ज्ञानकोश',''],
                ['scriptures','ॐ','ग्रंथसंदर्भ',''],
                ['','◇','चार कुंभक्षेत्रे','#four-centres'],
            ] as [$route,$icon,$label,$fragment]): ?>
                <a href="<?= tk_kumbh_e(tk_kumbh_url($route).$fragment) ?>"><span aria-hidden="true"><?= tk_kumbh_e($icon) ?></span><?= tk_kumbh_e($label) ?></a>
            <?php endforeach; ?>
        </nav>
        <div class="tk-km-editorial">
            <p class="tk-km-eyebrow">यात्रेची तयारी</p>
            <h2 id="choose-venue">स्नान केंद्र निवडा</h2>
            <p>तारीख, स्नानस्थळ आणि प्रवेश सूचना केंद्रानुसार वेगळ्या आहेत.</p>
            <div class="tk-km-venues">
                <section><p class="tk-km-eyebrow">०१ · गोदावरी</p><h3>नाशिक</h3><p>रामतीर्थ व पंचवटी. स्नान आणि प्रवासासाठी नाशिकच्या सूचना वेगळ्या तपासा.</p><?php tk_kumbh_link('nashik','नाशिक यात्रा मार्गदर्शक →'); ?></section>
                <section><p class="tk-km-eyebrow">०२ · ब्रह्मगिरी</p><h3>त्र्यंबकेश्वर</h3><p>कुशावर्त तीर्थ, त्र्यंबकेश्वर ज्योतिर्लिंग व ब्रह्मगिरी. प्रवेश सूचना स्वतंत्र आहेत.</p><?php tk_kumbh_link('trimbakeshwar','त्र्यंबकेश्वर यात्रा मार्गदर्शक →'); ?></section>
            </div>
            <h2 id="four-centres">भारतातील चार कुंभक्षेत्रे</h2>
            <div class="tk-kumbh-nav"><?php foreach (['prayagraj'=>'प्रयागराज','haridwar'=>'हरिद्वार','ujjain'=>'उज्जैन','nashik-trimbakeshwar'=>'नाशिक–त्र्यंबकेश्वर'] as $k=>$label) tk_kumbh_link($k,$label); ?></div>
            <h2>कुंभाचा अभ्यास</h2>
            <div class="tk-kumbh-nav"><?php tk_kumbh_link('faq'); tk_kumbh_link('scriptures','सिंहस्थ का म्हणतात?','#simhastha'); tk_kumbh_link('history'); tk_kumbh_link('media'); ?></div>
            <details class="tk-km-credits">
                <summary>संग्रहित छायाचित्रे व श्रेय</summary>
                <p>ही संग्रहित छायाचित्रे आहेत; सध्याची गर्दी किंवा प्रवेशस्थिती दाखवत नाहीत. मांडणीसाठी दृश्य कापले आहे.</p>
                <ul><?php foreach ($photos as [$route,$label,$alt,$hash,$file,$credit,$year]): ?>
                    <li><a href="https://commons.wikimedia.org/wiki/File:<?= tk_kumbh_e(rawurlencode($file)) ?>"><?= tk_kumbh_e($label.' — '.$credit.' ('.$year.')') ?></a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></li>
                <?php endforeach; ?></ul>
            </details>
        </div>
    <?php elseif ($key === 'calendar'): tk_kumbh_calendar($today); ?>
    <?php elseif ($key === 'nashik' || $key === 'trimbakeshwar'): $nashik = $key === 'nashik'; ?>
        <p><?= $nashik ? 'रामतीर्थ हे नाशिकच्या अधिकृत स्नान दिनदर्शिकेतील स्थळ आहे. पंचवटीचा रामायणाशी संबंध स्वतंत्रपणे वाचा.' : 'कुशावर्त तीर्थ हे त्र्यंबकेश्वरच्या अधिकृत स्नान दिनदर्शिकेतील स्थळ. ज्योतिर्लिंग आणि ब्रह्मगिरी ही स्वतंत्र दर्शनस्थळे आहेत.' ?></p>
        <h2>कसे पोहोचाल</h2>
        <p><?= $nashik ? 'रेल्वे प्रवासासाठी नाशिक रोडचा पर्याय पहा. रेल्वे स्थानक ते घाट यासाठी त्या दिवसाचे शहरातील मार्ग व वाहन निर्बंध तपासा.' : 'बहुतेक प्रवासांसाठी नाशिक हा प्रवेशबिंदू आहे. तेथून त्र्यंबकेश्वरचा पुढील रस्ता प्रवास आणि परतीची व्यवस्था आधी ठरवा.' ?></p>
        <p><?php tk_kumbh_source('how-to-reach','अधिकृत रेल्वे, रस्ता व विमान मार्गदर्शक'); ?> · <?php tk_kumbh_source('directions-to-ghats-and-parking','अधिकृत घाट व पार्किंग दिशानिर्देश'); ?></p>
        <h2>प्रवेश, सुविधा व सुलभता</h2>
        <p>पार्किंग, शटल, सार्वजनिक स्नान गेट, वैद्यकीय मदत, पिण्याचे पाणी, शौचालये आणि सुलभ मार्ग यासाठी प्रवासाच्या दिवशी अधिकृत सूचना तपासा. या पानावर अप्रमाणित व्यवस्था दिलेल्या नाहीत.</p>
        <p>ब्राउझरच्या Print पर्यायाने हा मजकूर छापा; छापील प्रत वापरण्यापूर्वी सूचना पुन्हा तपासा.</p>
        <div class="tk-kumbh-nav"><?php tk_kumbh_link('calendar','केंद्राची दिनदर्शिका','?venue='.$key); tk_kumbh_link('help'); tk_kumbh_link('scriptures',$nashik ? 'पंचवटीचा ग्रंथसंदर्भ' : 'कुशावर्ताचा ग्रंथसंदर्भ',$nashik ? '#panchavati' : '#kushavarta'); ?></div>
    <?php elseif ($key === 'faq'):
        $raw = $_GET['q'] ?? '';
        $query = is_string($raw) ? mb_substr(trim($raw),0,100) : '';
        $q = $query;
        if (in_array(mb_strtolower($q), ['kushavarta','kushawarta','kushavart'], true)) $q = 'कुशावर्त';
        $groups = [];
        foreach (tk_kumbh_records('faq') as $group) {
            $group['id'] = (int)$group['questions'][0]['id'];
            $group['questions'] = array_filter($group['questions'], static fn(array $item): bool => $q === '' || mb_stripos($group['title'].' '.$item['q'].' '.$item['a'],$q) !== false);
            if ($group['questions']) $groups[] = $group;
        }
        ?>
        <form method="get" action="<?= tk_kumbh_e(tk_kumbh_url('faq')) ?>" class="tk-kumbh-tools tk-km-search">
            <label for="tk-kumbh-q">प्रश्न शोधा</label>
            <div><input type="search" id="tk-kumbh-q" name="q" value="<?= tk_kumbh_e($query) ?>" maxlength="100" placeholder="उदा. कुशावर्त किंवा Kushavarta">
            <button type="submit">शोधा</button></div>
            <?php if ($query !== '') tk_kumbh_link('faq','सर्व प्रश्न'); ?>
        </form>
        <?php if ($query !== '' && $groups): ?><p>जुळलेले प्रश्न: <?= array_sum(array_map(static fn(array $g): int => count($g['questions']), $groups)) ?></p><?php endif; ?>
        <?php if ($groups): ?>
        <div class="tk-km-knowledge">
            <nav aria-label="ज्ञानकोशाचे विषय"><strong>विषय</strong>
                <?php foreach ($groups as $group): ?><a href="#topic-<?= $group['id'] ?>"><?= tk_kumbh_e($group['title']) ?></a><?php endforeach; ?>
            </nav>
            <div>
            <?php foreach ($groups as $group): ?>
                <section class="tk-km-topic" id="topic-<?= $group['id'] ?>"><h2><?= tk_kumbh_e($group['title']) ?></h2>
                <?php foreach ($group['questions'] as $item): ?>
                    <details class="tk-km-disclosure"<?= $query !== '' ? ' open' : '' ?>>
                        <summary><?= tk_kumbh_e($item['q']) ?></summary>
                        <div class="tk-km-answer" id="q-<?= (int)$item['id'] ?>"><p><?= tk_kumbh_e($item['a']) ?></p><a href="<?= tk_kumbh_e(tk_kumbh_url('faq').'#q-'.(int)$item['id']) ?>">या प्रश्नाचा दुवा</a></div>
                    </details>
                <?php endforeach; ?>
                <p class="tk-km-topic-source"><?php tk_kumbh_source($group['source'],'विषयाचा संदर्भ'); ?></p></section>
            <?php endforeach; ?>
            </div>
        </div>
        <?php else: ?><p>या शोधाशी जुळणारा प्रश्न सापडला नाही.</p><?php endif; ?>
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
