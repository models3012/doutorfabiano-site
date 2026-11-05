"""Gera as páginas de tratamento e de políticas a partir do index.html.

Uso:  python tools/gerar_paginas.py
O cabeçalho, o rodapé e o botão de WhatsApp são copiados do index.html,
então qualquer mudança neles vale para todas as páginas ao rodar de novo.
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://doutorfabiano.help"
TODAY = date.today().isoformat()
WA = "https://wa.me/5562995540548"

# Enquanto o site for prévia, as páginas ficam fora do Google. No lançamento, troque para False.
PREVIEW = True

index = (ROOT / "index.html").read_text(encoding="utf-8")


def absolutize(html: str) -> str:
    html = re.sub(r'href="#([\w-]+)"', r'href="/#\1"', html)
    html = re.sub(r'(src|href)="(images|favicon)', r'\1="/\2', html)
    html = html.replace('class="to-top" href="/#inicio"', 'class="to-top" href="#topo"')
    return html


HEADER = absolutize(re.search(r'<header class="site-header".*?</header>', index, re.S).group(0))
FOOTER = absolutize(re.search(r'<!-- ============ FOOTER ============ -->.*?(?=<script src="script\.js")', index, re.S).group(0))
HEAD_LINKS = re.search(r'<link rel="preconnect".*?<link rel="stylesheet" href="styles\.css">', index, re.S).group(0)
HEAD_LINKS = HEAD_LINKS.replace('href="styles.css"', 'href="/styles.css"')

ORG_REF = {"@id": f"{SITE}/#clinica"}


def head(title, description, path, image, schema):
    robots = '\n  <meta name="robots" content="noindex, nofollow">' if PREVIEW else ""
    url = f"{SITE}{path}"
    schemas = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#0A1422">{robots}
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/favicon.svg">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Dr. Fabiano Odontologia">
  <meta property="og:image" content="{SITE}{image}">
  <meta name="twitter:card" content="summary_large_image">
  {HEAD_LINKS}
  <script>document.documentElement.classList.add('js')</script>
{schemas}
</head>
<body>

<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
"""


def tail():
    return f"""
{FOOTER}<script src="/script.js" defer></script>
</body>
</html>
"""


def breadcrumb(items):
    crumbs = []
    for i, (name, path) in enumerate(items):
        if path and i < len(items) - 1:
            crumbs.append(f'<a href="{path}">{name}</a>')
        else:
            crumbs.append(f'<span aria-current="page">{name}</span>')
    html = '<nav class="breadcrumb" aria-label="Você está em">' + '<i class="ph-light ph-caret-right" aria-hidden="true"></i>'.join(crumbs) + "</nav>"
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{SITE}{path}"}
            for i, (name, path) in enumerate(items)
        ],
    }
    return html, schema


def faq_html(faqs):
    items = "\n".join(
        f"""      <details>
        <summary>{q}<i class="ph-light ph-plus" aria-hidden="true"></i></summary>
        <p>{a}</p>
      </details>"""
        for q, a in faqs
    )
    return items


def faq_schema(faqs):
    strip = lambda s: re.sub(r"<[^>]+>", "", s).replace("&amp;", "&")
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in faqs
        ],
    }


SIDE_CARD = f"""<aside class="side-card">
        <p class="eyebrow">Atendimento em Goiânia</p>
        <p class="side-title">Agende sua avaliação com escaneamento 3D</p>
        <a class="btn btn-gold" data-wa href="{WA}"><i class="ph-light ph-whatsapp-logo" aria-hidden="true"></i> Agendar pelo WhatsApp</a>
        <ul class="side-list">
          <li><i class="ph-light ph-phone" aria-hidden="true"></i><a href="tel:+5562995540548">(62) 99554-0548</a></li>
          <li><i class="ph-light ph-map-pin" aria-hidden="true"></i><span>Setor Bueno, Goiânia/GO</span></li>
          <li><i class="ph-light ph-clock" aria-hidden="true"></i><span>Seg a sex, 8h às 20h · Sáb, 8h às 13h</span></li>
          <li><i class="ph-light ph-credit-card" aria-hidden="true"></i><span>Parcelamento em até 36x</span></li>
        </ul>
      </aside>"""

FINANCE_LINE = '<p class="page-finance"><strong>Até 36x</strong> no crediário BrasilCard, sujeito a análise de crédito.</p>'


def price_block(kind, wa_label):
    if kind == "implante":
        body = """<dl class="price-lines">
            <div><dt>Cirurgia de implante</dt><dd>R$ 850</dd></div>
            <div><dt>Coroa de porcelana</dt><dd>R$ 850</dd></div>
          </dl>
          <p class="price-total"><span>Total por elemento</span><strong>R$ 1.700</strong></p>"""
    elif kind == "lentes":
        body = """<p class="price-from"><span>Dentes de porcelana a partir de</span><strong>R$ 1.300</strong></p>
          <p class="price-note">O valor varia de acordo com a quantidade de dentes.</p>"""
    else:
        body = """<p class="price-from"><span>Valor do tratamento</span><strong class="price-word">definido na avaliação</strong></p>
          <p class="price-note">O orçamento depende do planejamento do seu caso e é apresentado com todas as etapas.</p>"""
    return f"""<div class="page-price">
          {body}
          {FINANCE_LINE}
          <a class="btn btn-gold" data-wa="{wa_label} (valores)" href="{WA}">Receber meu orçamento</a>
          <p class="price-disclaimer">Valores de referência, sujeitos a avaliação clínica.</p>
        </div>"""


TREATMENTS = [
    {
        "slug": "implante-dentario-goiania",
        "name": "Implante dentário",
        "title": "Implante Dentário em Goiânia | Dr. Fabiano",
        "description": "Implante dentário em Goiânia com cirurgia guiada por tomografia e opção de carga imediata. Avaliação com escaneamento 3D no Setor Bueno. Agende pelo WhatsApp.",
        "h1": "Implante dentário em Goiânia",
        "eyebrow": "Implantodontia",
        "intro": "Recupere a função e a estética do sorriso com implantes de titânio planejados por tomografia. No Setor Bueno, em Goiânia, cada implante é colocado com cirurgia guiada e acompanhamento do início ao fim.",
        "image": ("/images/valores/implante-coroa-porcelana-foto.webp", "Implante dentário de titânio com coroa de porcelana em Goiânia", 656, 820, "50% 40%"),
        "og": "/images/valores/implante-coroa-porcelana-foto.webp",
        "price": "implante",
        "case": None,
        "sections": [
            ("O que é o implante dentário", [
                "O implante é um pino de titânio colocado no osso, no lugar da raiz do dente perdido. Depois que ele se integra ao osso, recebe uma coroa de porcelana feita sob medida, com cor e formato pensados para combinar com os outros dentes.",
                "O resultado é um dente fixo, firme para mastigar e natural no sorriso, sem depender dos dentes vizinhos como acontece em uma ponte.",
            ], None),
            ("Para quem é indicado", [
                "Para quem perdeu um ou mais dentes, usa prótese removível e quer algo fixo, ou tem dentes condenados que precisam ser extraídos. A quantidade e a qualidade do osso são avaliadas na tomografia.",
            ], ["Perda de um dente isolado", "Perda de vários dentes ou da arcada inteira (protocolo)", "Quem não se adaptou à dentadura removível"]),
            ("Como funciona o tratamento", [
                "O tratamento segue etapas bem definidas, e você sabe o que vai acontecer em cada uma delas.",
            ], ["Avaliação com tomografia e escaneamento 3D", "Planejamento digital da posição de cada implante", "Cirurgia guiada, com anestesia indolor e opção de sedação consciente", "Período de integração ao osso, em geral de 3 a 6 meses", "Instalação da coroa definitiva de porcelana"]),
            ("Carga imediata: dentes fixos em poucos dias", [
                "Quando o osso tem boa estabilidade, é possível instalar um dente provisório fixo no mesmo dia ou poucos dias depois da cirurgia. Assim você não fica sem dente durante a integração. A indicação é confirmada na avaliação.",
            ], None),
            ("Tecnologia e segurança", [
                "A tomografia mostra o osso em três dimensões, e o guia cirúrgico leva o implante exatamente para a posição planejada. Isso deixa a cirurgia mais rápida, mais previsível e com menos desconforto no pós-operatório.",
            ], None),
        ],
        "faqs": [
            ("Implante dentário dói?", "A cirurgia é feita com anestesia local e você não sente dor durante o procedimento. Para quem tem medo, oferecemos sedação consciente com óxido nitroso. O pós-operatório costuma ser tranquilo, com medicação simples."),
            ("Quanto tempo dura um implante?", "Com higiene adequada e revisões periódicas, o implante pode durar a vida toda. A coroa de porcelana tem durabilidade média de 15 a 20 anos."),
            ("Quem tem pouco osso pode fazer implante?", "Muitas vezes sim. Dependendo do caso, é possível fazer enxerto ósseo ou usar implantes de tamanhos específicos. A tomografia mostra qual é o melhor caminho."),
            ("Quanto custa um implante dentário em Goiânia?", "Como referência, a cirurgia de implante é R$ 850 e a coroa de porcelana R$ 850, total de R$ 1.700 por elemento. O valor final depende do número de implantes e da necessidade de enxerto, e pode ser parcelado em até 36x."),
        ],
    },
    {
        "slug": "protese-fixa-goiania",
        "name": "Prótese fixa e protocolo",
        "title": "Prótese Fixa e Protocolo em Goiânia | Dr. Fabiano",
        "description": "Prótese fixa e protocolo dentário em Goiânia: dentes fixos apoiados nos dentes naturais ou em implantes. Planejamento digital no Setor Bueno. Agende pelo WhatsApp.",
        "h1": "Prótese fixa e protocolo em Goiânia",
        "eyebrow": "Prótese dentária",
        "intro": "Dentes fixos, estáveis e com aparência natural. A prótese fixa pode ser apoiada nos seus próprios dentes ou em implantes, e o planejamento mostra qual opção faz mais sentido para o seu caso.",
        "image": ("/images/valores/protese-fixa-foto.webp", "Prótese fixa apoiada nos dentes naturais", 836, 627, "50% 50%"),
        "og": "/images/valores/protese-fixa-foto.webp",
        "price": "geral",
        "case": None,
        "sections": [
            ("O que é a prótese fixa", [
                "A prótese fixa, também chamada de ponte, repõe um ou mais dentes usando os dentes vizinhos como apoio. Eles recebem um preparo e a ponte de porcelana é cimentada sobre eles. Você não tira a prótese para dormir nem para limpar.",
            ], None),
            ("Prótese fixa ou protocolo: qual a diferença", [
                "A prótese fixa tradicional se apoia nos dentes naturais e serve para repor poucos dentes. O protocolo é uma arcada inteira fixa, parafusada sobre 4 a 6 implantes, indicada para quem perdeu todos os dentes de cima ou de baixo.",
            ], None),
            ("Para quem é indicada", [
                "Para quem perdeu dentes e quer uma solução fixa, tem dentes vizinhos saudáveis que podem servir de apoio ou não se adapta à dentadura removível.",
            ], ["Perda de 1 a 3 dentes seguidos", "Arcada sem dentes (protocolo sobre implantes)", "Substituição de pontes antigas e desgastadas"]),
            ("Como é feita", [
                "Depois da avaliação e do escaneamento 3D, os dentes de apoio são preparados e você sai com uma prótese provisória. A definitiva é feita em laboratório com cor e formato planejados e cimentada em seguida.",
            ], None),
            ("Cuidados e durabilidade", [
                "A higiene inclui fio dental passado por baixo da ponte, com passa-fio, e revisões periódicas. Com esses cuidados, uma prótese fixa de porcelana costuma durar de 10 a 15 anos ou mais.",
            ], None),
        ],
        "faqs": [
            ("Qual a diferença entre prótese fixa e protocolo?", "A prótese fixa se apoia nos dentes naturais e repõe poucos dentes. O protocolo é uma arcada completa fixa sobre implantes, para quem perdeu todos os dentes de uma arcada."),
            ("Preciso de implante para ter dentes fixos?", "Nem sempre. Se os dentes vizinhos estiverem saudáveis, a prótese fixa pode ser apoiada neles, sem cirurgia. A avaliação mostra se essa é a melhor opção."),
            ("Quanto tempo dura uma prótese fixa?", "Em média de 10 a 15 anos ou mais, com boa higiene e revisões a cada 6 meses."),
            ("Quanto custa uma prótese fixa em Goiânia?", "O valor depende do número de dentes, do material e do tipo de apoio. O orçamento é apresentado na avaliação, e o tratamento pode ser parcelado em até 36x."),
        ],
    },
    {
        "slug": "lentes-de-contato-dental-goiania",
        "name": "Lentes de contato dental",
        "title": "Lentes de Contato Dental em Goiânia | Dr. Fabiano",
        "description": "Lentes de contato dental e facetas de porcelana em Goiânia, com ensaio do novo sorriso antes de começar. Planejamento digital no Setor Bueno. Agende pelo WhatsApp.",
        "h1": "Lentes de contato dental em Goiânia",
        "eyebrow": "Odontologia estética",
        "intro": "Lâminas de porcelana ultrafinas que corrigem cor, formato e pequenos desalinhamentos com mínimo ou nenhum desgaste. Você vê e aprova o novo sorriso antes do tratamento começar.",
        "image": ("/images/valores/dentes-de-porcelana-foto.webp", "Sorriso com lentes de contato dental em porcelana em Goiânia", 796, 597, "50% 50%"),
        "og": "/images/casos/lentes-depois.webp",
        "price": "lentes",
        "case": "lentes",
        "sections": [
            ("O que são as lentes de contato dental", [
                "São lâminas de porcelana com 0,2 a 0,5 mm de espessura, coladas na frente dos dentes. Elas mudam a cor, o formato e o comprimento dos dentes, fecham pequenos espaços e deixam o sorriso harmônico com o rosto.",
            ], None),
            ("Lentes ou facetas: qual a diferença", [
                "As lentes são mais finas e quase sempre dispensam desgaste. As facetas são um pouco mais espessas e indicadas quando é preciso corrigir mais cor ou mais formato. As duas são feitas em porcelana e o planejamento define a melhor opção para cada dente.",
            ], None),
            ("Para quem é indicado", [
                "Para quem quer mudar o sorriso de forma duradoura e natural.",
            ], ["Dentes manchados que não respondem ao clareamento", "Espaços entre os dentes (diastemas)", "Dentes pequenos, desgastados ou com formato irregular", "Pequenos desalinhamentos"]),
            ("Como funciona o tratamento", [
                "O sorriso é desenhado no computador (Digital Smile Design) e testado na sua boca com um ensaio provisório, o mock-up. Só depois da sua aprovação as lentes são produzidas e cimentadas, em média em 3 sessões.",
            ], None),
            ("Durabilidade e cuidados", [
                "Com escovação, fio dental e revisões periódicas, as lentes de porcelana duram de 15 a 20 anos. A porcelana não mancha com café ou vinho. Para quem range os dentes, indicamos uma placa de proteção noturna.",
            ], None),
        ],
        "faqs": [
            ("Lente de contato desgasta o dente?", "Na maioria dos casos o desgaste é mínimo ou nenhum. A avaliação define a técnica certa para o seu sorriso."),
            ("Quanto tempo dura uma lente de porcelana?", "De 15 a 20 anos, com higiene adequada e revisões periódicas."),
            ("O resultado fica natural?", "Sim. Cor, formato e translucidez são planejados para o seu rosto, e você aprova o resultado no ensaio antes da cimentação."),
            ("Quanto custa lente de contato dental em Goiânia?", "Os dentes de porcelana começam em R$ 1.300 e o valor varia de acordo com a quantidade de dentes. O tratamento pode ser parcelado em até 36x."),
        ],
    },
    {
        "slug": "clareamento-dental-goiania",
        "name": "Clareamento dental",
        "title": "Clareamento Dental a Laser em Goiânia | Dr. Fabiano",
        "description": "Clareamento dental a laser em Goiânia com controle de sensibilidade e resultado já na primeira sessão. Atendimento no Setor Bueno. Agende pelo WhatsApp.",
        "h1": "Clareamento dental em Goiânia",
        "eyebrow": "Estética dental",
        "intro": "Dentes mais claros com segurança, sem agredir o esmalte. O clareamento a laser em consultório mostra resultado já na primeira sessão, com protocolo para controlar a sensibilidade.",
        "image": ("/images/casos/clareamento-depois-m.webp", "Resultado de clareamento dental a laser em Goiânia", 1000, 563, "50% 50%"),
        "og": "/images/casos/clareamento-depois.webp",
        "price": "geral",
        "case": "clareamento",
        "sections": [
            ("Como funciona o clareamento a laser", [
                "Um gel clareador é aplicado sobre os dentes e ativado por luz, o que acelera a reação. A gengiva é protegida antes da aplicação e todo o processo é acompanhado pelo dentista.",
            ], None),
            ("Clareamento em consultório ou caseiro", [
                "O clareamento em consultório traz resultado mais rápido. O caseiro usa moldeiras feitas sob medida e gel em concentração menor por algumas semanas. Muitas vezes a combinação dos dois dá o melhor resultado, e isso é definido na avaliação.",
            ], None),
            ("Para quem é indicado", [
                "Para quem tem dentes amarelados pelo tempo, por café, chá, vinho ou cigarro. Antes de clarear, avaliamos cáries, gengiva e sensibilidade para garantir um tratamento seguro.",
            ], None),
            ("Sensibilidade sob controle", [
                "Usamos géis com dessensibilizantes e ajustamos o protocolo para cada paciente. Quando aparece, a sensibilidade é leve e passageira.",
            ], None),
            ("Quanto tempo dura o resultado", [
                "O resultado costuma durar de 1 a 3 anos, dependendo dos hábitos. Uma manutenção periódica mantém a cor por muito mais tempo.",
            ], None),
        ],
        "faqs": [
            ("Clareamento dental dói?", "Não dói. Algumas pessoas sentem uma sensibilidade leve e passageira, que controlamos com gel dessensibilizante."),
            ("Quantas sessões são necessárias?", "No consultório, em geral de 1 a 3 sessões, dependendo da cor inicial e do resultado desejado."),
            ("Clareamento estraga o esmalte?", "Não. Feito com acompanhamento profissional e produtos regulamentados, o clareamento é seguro para o esmalte."),
            ("Dá para clarear lentes, coroas ou restaurações?", "Não. Porcelana e resina não mudam de cor com o clareamento. Se você tem restaurações na frente, planejamos a troca depois de clarear."),
        ],
    },
    {
        "slug": "invisalign-goiania",
        "name": "Invisalign",
        "title": "Invisalign em Goiânia | Alinhadores | Dr. Fabiano",
        "description": "Invisalign e alinhadores transparentes em Goiânia, com simulação digital do resultado antes de começar. Atendimento no Setor Bueno. Agende pelo WhatsApp.",
        "h1": "Invisalign e alinhadores em Goiânia",
        "eyebrow": "Ortodontia invisível",
        "intro": "Dentes alinhados sem bráquetes nem fios. Os alinhadores são transparentes, removíveis e planejados digitalmente, e você vê a simulação do resultado final antes de começar.",
        "image": ("/images/casos/invisalign-depois-m.webp", "Dentes alinhados com Invisalign em Goiânia", 1000, 563, "50% 50%"),
        "og": "/images/casos/invisalign-depois.webp",
        "price": "geral",
        "case": "invisalign",
        "sections": [
            ("O que é o Invisalign", [
                "É um sistema de alinhadores transparentes feitos sob medida a partir do escaneamento 3D dos seus dentes. Cada alinhador faz um pequeno movimento, até chegar à posição planejada.",
            ], None),
            ("Para quem é indicado", [
                "Para adultos e adolescentes que querem corrigir o sorriso de forma discreta.",
            ], ["Dentes apinhados ou tortos", "Espaços entre os dentes", "Mordida cruzada, aberta ou profunda, conforme avaliação", "Recidiva de aparelho antigo"]),
            ("Como funciona o tratamento", [
                "Depois do escaneamento, o planejamento digital mostra cada etapa do movimento dos dentes. Você troca de alinhador a cada 1 ou 2 semanas e faz revisões periódicas na clínica.",
            ], ["Uso de 20 a 22 horas por dia", "Retire para comer e escovar os dentes", "Sem emergências com bráquetes soltos ou fios machucando"]),
            ("Vantagens em relação ao aparelho fixo", [
                "Os alinhadores são quase invisíveis, não limitam a alimentação e facilitam a higiene. Também são mais confortáveis, sem peças metálicas em contato com a bochecha.",
            ], None),
            ("Tempo de tratamento", [
                "Varia de 6 a 18 meses, dependendo da complexidade do caso. Ao final, usamos uma contenção para manter os dentes na nova posição.",
            ], None),
        ],
        "faqs": [
            ("Invisalign dói?", "Nos primeiros dias de cada alinhador você pode sentir uma pressão leve, sinal de que os dentes estão se movendo. Não é dor intensa."),
            ("Quanto tempo dura o tratamento?", "De 6 a 18 meses na maioria dos casos. O planejamento digital mostra a previsão para você antes de começar."),
            ("Posso comer com os alinhadores?", "Não. Você retira para comer, escova os dentes e coloca de volta. Isso evita manchas e mantém a higiene."),
            ("Preciso usar contenção depois?", "Sim. A contenção mantém os dentes na posição nova e é parte importante do resultado."),
        ],
    },
    {
        "slug": "harmonizacao-orofacial-goiania",
        "name": "Harmonização orofacial",
        "title": "Harmonização Orofacial em Goiânia | Dr. Fabiano",
        "description": "Harmonização orofacial em Goiânia com toxina botulínica, preenchedores e bioestimuladores, aplicados com critério e resultado natural. Agende pelo WhatsApp.",
        "h1": "Harmonização orofacial em Goiânia",
        "eyebrow": "Estética da face",
        "intro": "Equilíbrio entre sorriso e rosto, com resultado natural. A harmonização orofacial usa procedimentos minimamente invasivos para suavizar linhas, devolver volume e realçar seus traços, sem exageros.",
        "image": ("/images/dr-fabiano.jpg", "Dr. Fabiano, cirurgião-dentista com atuação em harmonização orofacial em Goiânia", 900, 931, "50% 30%"),
        "image_fallback": "/images/casos/facetas-depois-m.webp",
        "og": "/images/casos/facetas-depois.webp",
        "price": "geral",
        "case": None,
        "sections": [
            ("O que é a harmonização orofacial", [
                "É um conjunto de procedimentos que equilibra as proporções da face, principalmente do terço inferior: lábios, queixo, mandíbula e região ao redor da boca. A harmonização orofacial é uma especialidade odontológica reconhecida pelo CFO.",
            ], None),
            ("Procedimentos realizados", [
                "Cada plano é individual e pode combinar diferentes técnicas.",
            ], ["Toxina botulínica para linhas de expressão e sorriso gengival", "Preenchimento com ácido hialurônico para lábios, olheiras e contorno", "Bioestimuladores de colágeno para firmeza da pele", "Tratamento do bruxismo com toxina botulínica"]),
            ("Para quem é indicada", [
                "Para quem quer suavizar sinais do tempo, corrigir pequenas assimetrias ou completar o resultado de um tratamento no sorriso, como lentes de contato dental.",
            ], None),
            ("Segurança em primeiro lugar", [
                "Usamos produtos aprovados pela Anvisa e técnicas com cânulas que reduzem o risco de hematomas. Antes de qualquer aplicação, avaliamos a face, o histórico de saúde e as suas expectativas.",
            ], None),
            ("Resultados naturais e duradouros", [
                "O objetivo é você parecer descansado, não diferente. A toxina botulínica dura de 4 a 6 meses e os preenchimentos de 12 a 18 meses, em média.",
            ], None),
        ],
        "faqs": [
            ("Dentista pode fazer harmonização orofacial?", "Sim. A harmonização orofacial é uma especialidade odontológica reconhecida pelo Conselho Federal de Odontologia."),
            ("A aplicação dói?", "O desconforto é pequeno. Usamos anestésico tópico e, quando indicado, anestesia local."),
            ("Quanto tempo dura o resultado?", "A toxina botulínica dura de 4 a 6 meses. Os preenchedores com ácido hialurônico duram de 12 a 18 meses, em média."),
            ("O resultado fica artificial?", "Não deve ficar. Trabalhamos com doses e volumes conservadores para manter as suas expressões e a naturalidade do rosto."),
        ],
    },
]


def treatment_page(t):
    path = f"/{t['slug']}/"
    crumbs_html, crumbs_schema = breadcrumb([("Início", "/"), ("Tratamentos", "/#tratamentos"), (t["h1"], path)])
    img, alt, w, h, pos = t["image"]
    fallback = f""" onerror="this.onerror=null;this.src='{t['image_fallback']}'" """.rstrip() if t.get("image_fallback") else ""

    sections = []
    for title, paras, bullets in t["sections"]:
        body = "\n".join(f"        <p>{p}</p>" for p in paras)
        if bullets:
            body += "\n        <ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
        sections.append(f"      <section>\n        <h2>{title}</h2>\n{body}\n      </section>")

    case = ""
    if t["case"]:
        c = t["case"]
        case = f"""
      <section>
        <h2>Antes e depois</h2>
        <div class="ba-pair">
          <figure><img src="/images/casos/{c}-antes-m.webp" alt="Antes do tratamento de {t['name'].lower()} – Dr. Fabiano, Goiânia" width="1000" height="563" loading="lazy" decoding="async"><figcaption>Antes</figcaption></figure>
          <figure><img src="/images/casos/{c}-depois-m.webp" alt="Depois do tratamento de {t['name'].lower()} – Dr. Fabiano, Goiânia" width="1000" height="563" loading="lazy" decoding="async"><figcaption>Depois</figcaption></figure>
        </div>
        <p class="ba-note">Imagens demonstrativas. Resultados variam de acordo com cada caso e avaliação clínica. <a href="/#transformacoes">Ver mais transformações</a></p>
      </section>"""

    related = "\n".join(
        f"""      <a class="related-card reveal" href="/{o['slug']}/"><span>{o['eyebrow']}</span><strong>{o['h1']}</strong><i class="ph-light ph-arrow-right" aria-hidden="true"></i></a>"""
        for o in TREATMENTS if o["slug"] != t["slug"]
    )

    procedure_schema = {
        "@context": "https://schema.org",
        "@type": "MedicalProcedure",
        "name": t["name"],
        "url": f"{SITE}{path}",
        "description": t["description"],
        "provider": ORG_REF,
        "areaServed": {"@type": "City", "name": "Goiânia"},
    }
    page = head(t["title"], t["description"], path, t["og"], [procedure_schema, crumbs_schema, faq_schema(t["faqs"])])
    page += f"""
{HEADER}

<main id="conteudo">

<section class="page-hero">
  <div class="hero-bg" aria-hidden="true"></div>
  <div class="container page-hero-grid">
    <div class="page-hero-copy">
      {crumbs_html}
      <p class="eyebrow">{t['eyebrow']} · Goiânia</p>
      <h1 class="page-title">{t['h1']}</h1>
      <p class="page-intro">{t['intro']}</p>
      <div class="hero-ctas">
        <a class="btn btn-gold btn-lg" data-wa="{t['name']}" href="{WA}"><i class="ph-light ph-whatsapp-logo" aria-hidden="true"></i> Agendar avaliação</a>
        <a class="btn btn-ghost btn-lg" href="#investimento">Ver valores <i class="ph-light ph-arrow-down" aria-hidden="true"></i></a>
      </div>
    </div>
    <div class="page-hero-media">
      <img src="{img}" alt="{alt}" width="{w}" height="{h}" fetchpriority="high" style="object-position: {pos}"{fallback}>
    </div>
  </div>
</section>

<div class="section section-white">
  <div class="container article-grid">
    <article class="prose">
{chr(10).join(sections)}{case}
      <section id="investimento">
        <h2>Investimento e formas de pagamento</h2>
        {price_block(t['price'], t['name'])}
      </section>
      <section>
        <h2>Perguntas frequentes sobre {t['name'].lower()}</h2>
        <div class="faq-list">
{faq_html(t['faqs'])}
        </div>
      </section>
    </article>
    {SIDE_CARD}
  </div>
</div>

<section class="section" aria-labelledby="outros">
  <div class="container">
    <header class="section-head reveal">
      <p class="eyebrow">Outros tratamentos</p>
      <h2 class="section-title" id="outros">Tratamentos em Goiânia</h2>
    </header>
    <div class="related-grid">
{related}
    </div>
  </div>
</section>

</main>
"""
    page += tail()
    return path, page


# ---------- Policy pages ----------
CLINIC_ID = """<p><strong>Dr. Fabiano Odontologia</strong> · Clínica Odontológica Dr. Fabiano Ltda. · CNPJ 00.000.000/0001-00 · CRO-GO EPAO 0000<br>
Responsável técnico: Dr. Fabiano · CRO-GO 00.000<br>
Endereço: Av. 0000, nº 000, Sala 000, Setor Bueno, Goiânia/GO, CEP 00000-000<br>
Contato: <a href="mailto:contato@doutorfabiano.help">contato@doutorfabiano.help</a> · <a href="tel:+5562995540548">(62) 99554-0548</a></p>"""

POLICIES = [
    {
        "slug": "politica-de-privacidade",
        "h1": "Política de Privacidade",
        "title": "Política de Privacidade | Dr. Fabiano Odontologia",
        "description": "Como a Dr. Fabiano Odontologia, em Goiânia, coleta, usa e protege seus dados pessoais, em conformidade com a LGPD (Lei 13.709/2018).",
        "body": f"""
      <p>Esta política explica como tratamos os seus dados pessoais quando você visita o site doutorfabiano.help, fala conosco pelo WhatsApp ou é atendido na clínica. Seguimos a Lei Geral de Proteção de Dados (Lei 13.709/2018, LGPD) e o Código de Ética Odontológica.</p>

      <h2>1. Quem é o controlador dos dados</h2>
      {CLINIC_ID}
      <p>Encarregado pelo tratamento de dados (DPO): Dr. Fabiano, pelo e-mail <a href="mailto:contato@doutorfabiano.help">contato@doutorfabiano.help</a>.</p>

      <h2>2. Quais dados coletamos</h2>
      <ul>
        <li><strong>Dados de contato:</strong> nome, telefone e as mensagens que você envia pelo WhatsApp ou por e-mail.</li>
        <li><strong>Dados de navegação:</strong> páginas visitadas, tipo de dispositivo e origem do acesso, somente se você aceitar os cookies de medição.</li>
        <li><strong>Dados de saúde:</strong> informações clínicas, exames, fotos e prontuário, coletados apenas no atendimento e tratados como dados sensíveis.</li>
      </ul>
      <p>O site não tem formulários e não coleta dados de pagamento.</p>

      <h2>3. Para que usamos os dados</h2>
      <ul>
        <li>Responder ao seu contato e agendar consultas.</li>
        <li>Prestar o atendimento odontológico e manter o prontuário.</li>
        <li>Cumprir obrigações legais e regulatórias, como as normas do Conselho Federal de Odontologia.</li>
        <li>Entender, de forma agregada, quais conteúdos do site são mais úteis, se você permitir.</li>
      </ul>

      <h2>4. Bases legais</h2>
      <p>Tratamos dados com base na execução de contrato e de procedimentos preliminares a pedido do titular (art. 7º, V), no cumprimento de obrigação legal (art. 7º, II), no legítimo interesse para responder contatos (art. 7º, IX) e no consentimento para cookies de medição (art. 7º, I). Dados de saúde são tratados para a tutela da saúde, por profissionais de saúde (art. 11, II, f).</p>

      <h2>5. Com quem compartilhamos</h2>
      <ul>
        <li><strong>WhatsApp (Meta):</strong> plataforma usada para a conversa que você inicia.</li>
        <li><strong>Google Analytics:</strong> somente se você aceitar os cookies de medição.</li>
        <li><strong>Hospedagem do site:</strong> GitHub Pages, que registra dados técnicos de acesso.</li>
        <li><strong>Laboratórios e parceiros clínicos</strong>, quando necessários ao seu tratamento.</li>
        <li><strong>Autoridades</strong>, quando exigido por lei.</li>
      </ul>
      <p>Alguns desses serviços podem armazenar dados fora do Brasil, com as garantias previstas no art. 33 da LGPD. Não vendemos dados pessoais.</p>

      <h2>6. Por quanto tempo guardamos</h2>
      <p>Mensagens de contato são guardadas pelo tempo necessário para o atendimento. O prontuário odontológico é guardado pelo prazo mínimo exigido pela legislação e pelas normas do CFO. Dados de navegação seguem os prazos descritos na <a href="/politica-de-cookies/">Política de Cookies</a>.</p>

      <h2>7. Seus direitos</h2>
      <p>Você pode pedir, a qualquer momento, a confirmação do tratamento, o acesso, a correção, a anonimização, a portabilidade ou a exclusão dos seus dados, além de revogar o consentimento (art. 18 da LGPD). Basta escrever para <a href="mailto:contato@doutorfabiano.help">contato@doutorfabiano.help</a>. Você também pode reclamar à Autoridade Nacional de Proteção de Dados (ANPD).</p>

      <h2>8. Segurança</h2>
      <p>Adotamos medidas técnicas e administrativas para proteger os dados contra acesso não autorizado, perda ou alteração, incluindo acesso restrito ao prontuário e conexão segura (HTTPS) no site.</p>

      <h2>9. Atualizações</h2>
      <p>Esta política pode ser atualizada. A data da última revisão aparece no fim desta página.</p>""",
    },
    {
        "slug": "politica-de-cookies",
        "h1": "Política de Cookies",
        "title": "Política de Cookies | Dr. Fabiano Odontologia",
        "description": "Quais cookies e tecnologias o site da Dr. Fabiano Odontologia usa, para que servem e como você controla as suas preferências.",
        "body": f"""
      <p>Cookies são pequenos arquivos guardados no seu navegador. Usamos o mínimo possível e só ativamos cookies de medição com a sua permissão.</p>

      <h2>1. Cookies e armazenamento que usamos</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Nome</th><th>Tipo</th><th>Finalidade</th><th>Duração</th></tr></thead>
          <tbody>
            <tr><td>drfabiano-cookies</td><td>Essencial</td><td>Guarda a sua escolha sobre cookies</td><td>Até você limpar o navegador</td></tr>
            <tr><td>_ga, _ga_*</td><td>Medição (Google Analytics)</td><td>Estatísticas agregadas de visitas e cliques no WhatsApp</td><td>Até 2 anos</td></tr>
          </tbody>
        </table>
      </div>
      <p>Os cookies de medição só são gravados se você clicar em <strong>Aceitar</strong> no aviso de cookies.</p>

      <h2>2. Serviços de terceiros</h2>
      <p>Para carregar fontes e ícones, o site acessa o Google Fonts e o unpkg. Esses serviços recebem dados técnicos, como o endereço IP, mas não gravam cookies de publicidade. Ao clicar nos botões de WhatsApp, você sai do site e passa a seguir as políticas da Meta.</p>

      <h2>3. Como mudar a sua escolha</h2>
      <p>Clique em <button type="button" class="link-button" data-cookie-settings>Preferências de cookies</button> para abrir o aviso de novo. Você também pode apagar os cookies nas configurações do seu navegador.</p>

      <h2>4. Contato</h2>
      {CLINIC_ID}""",
    },
    {
        "slug": "termos-de-uso",
        "h1": "Termos de Uso",
        "title": "Termos de Uso | Dr. Fabiano Odontologia",
        "description": "Condições de uso do site da Dr. Fabiano Odontologia, clínica odontológica em Goiânia.",
        "body": f"""
      <p>Ao usar o site doutorfabiano.help você concorda com estes termos. Se não concordar, recomendamos não utilizar o site.</p>

      <h2>1. Sobre o site</h2>
      <p>O site apresenta a clínica, os tratamentos oferecidos e os canais de contato. O conteúdo é informativo e <strong>não substitui a consulta, o diagnóstico ou a avaliação clínica presencial</strong>.</p>

      <h2>2. Agendamentos</h2>
      <p>Os botões do site abrem uma conversa no WhatsApp. O agendamento só é confirmado pela nossa equipe, de acordo com a disponibilidade da agenda.</p>

      <h2>3. Valores</h2>
      <p>Os valores informados no site são de referência e podem mudar sem aviso prévio. O orçamento válido é o apresentado por escrito após a avaliação clínica. Condições de parcelamento dependem de análise de crédito pela instituição financeira.</p>

      <h2>4. Imagens e resultados</h2>
      <p>As imagens de antes e depois são demonstrativas. Os resultados variam de pessoa para pessoa e dependem da avaliação, do planejamento e dos cuidados do paciente.</p>

      <h2>5. Propriedade intelectual</h2>
      <p>Textos, imagens, marca e layout pertencem à Dr. Fabiano Odontologia ou são usados com autorização. A reprodução sem permissão é proibida.</p>

      <h2>6. Links externos</h2>
      <p>O site pode ter links para serviços de terceiros, como WhatsApp e redes sociais, que têm políticas próprias.</p>

      <h2>7. Privacidade</h2>
      <p>O tratamento de dados pessoais segue a nossa <a href="/politica-de-privacidade/">Política de Privacidade</a>.</p>

      <h2>8. Legislação e foro</h2>
      <p>Estes termos seguem a legislação brasileira. Fica eleito o foro da comarca de Goiânia/GO, ressalvados os direitos do consumidor.</p>

      <h2>9. Contato</h2>
      {CLINIC_ID}""",
    },
    {
        "slug": "aviso-legal",
        "h1": "Aviso Legal",
        "title": "Aviso Legal e Responsabilidade Técnica | Dr. Fabiano Odontologia",
        "description": "Responsabilidade técnica, registro no CRO-GO e informações legais da Dr. Fabiano Odontologia, clínica odontológica em Goiânia.",
        "body": f"""
      <h2>1. Identificação e responsabilidade técnica</h2>
      {CLINIC_ID}

      <h2>2. Natureza do conteúdo</h2>
      <p>As informações deste site têm caráter educativo e informativo, conforme as normas de publicidade do Conselho Federal de Odontologia. Elas não constituem diagnóstico, indicação de tratamento ou promessa de resultado.</p>

      <h2>3. Resultados</h2>
      <p>Cada organismo responde de forma diferente aos tratamentos. Prazos, durabilidade e resultados citados são médias e só podem ser confirmados após avaliação clínica individual.</p>

      <h2>4. Imagens de pacientes</h2>
      <p>Imagens de pacientes só são publicadas com autorização por escrito, nos termos da Resolução CFO-196/2019. Neste momento, o site está em versão de demonstração e algumas imagens e textos são ilustrativos.</p>

      <h2>5. Depoimentos</h2>
      <p>Depoimentos refletem a experiência individual de cada paciente e não garantem o mesmo resultado para outras pessoas.</p>

      <h2>6. Emergências</h2>
      <p>Este site e o WhatsApp não são canais de emergência. Em caso de urgência médica, procure o pronto-socorro mais próximo ou ligue para o SAMU (192).</p>""",
    },
]


def policy_page(p):
    path = f"/{p['slug']}/"
    crumbs_html, crumbs_schema = breadcrumb([("Início", "/"), (p["h1"], path)])
    page = head(p["title"], p["description"], path, "/images/casos/lentes-depois.webp", [crumbs_schema])
    page += f"""
{HEADER}

<main id="conteudo">

<section class="page-hero page-hero-compact">
  <div class="hero-bg" aria-hidden="true"></div>
  <div class="container">
    {crumbs_html}
    <h1 class="page-title">{p['h1']}</h1>
  </div>
</section>

<div class="section section-white">
  <div class="container">
    <article class="prose prose-legal">
{p['body']}
      <p class="legal-updated">Última atualização: {date.today().strftime('%d/%m/%Y')}</p>
    </article>
  </div>
</div>

</main>
"""
    page += tail()
    return path, page


# ---------- Blog ----------
from html import escape

BLOG_DIR = ROOT / "tools" / "blog"
POSTS = sorted(
    (json.loads(p.read_text(encoding="utf-8")) for p in BLOG_DIR.glob("*.json")),
    key=lambda p: (p["date"], p["category"], p["slug"]),
    reverse=True,
)
CATEGORY_PAGE = {
    "Lentes de contato": ("/lentes-de-contato-dental-goiania/", "Lentes de contato dental em Goiânia"),
    "Implante dentário": ("/implante-dentario-goiania/", "Implante dentário em Goiânia"),
}


def read_minutes(body):
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return max(3, round(words / 200))


def br_date(iso):
    y, m, d = iso.split("-")
    months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    return f"{int(d)} de {months[int(m) - 1]} de {y}"


def post_card(p, extra_class=""):
    return f"""      <article class="post-card reveal{extra_class}" data-category="{escape(p['category'])}">
        <a href="/blog/{p['slug']}/">
          <div class="post-card-media"><img src="{p['image']}" alt="{escape(p['image_alt'])}" loading="lazy" decoding="async"></div>
          <div class="post-card-body">
            <p class="post-cat">{escape(p['category'])} · {read_minutes(p['body'])} min</p>
            <h3>{escape(p['h1'])}</h3>
            <p>{escape(p['excerpt'])}</p>
            <span class="post-more">Ler artigo <i class="ph-light ph-arrow-right" aria-hidden="true"></i></span>
          </div>
        </a>
      </article>"""


def blog_index():
    path = "/blog/"
    crumbs_html, crumbs_schema = breadcrumb([("Início", "/"), ("Blog", path)])
    cats = sorted({p["category"] for p in POSTS})
    filters = '<button type="button" class="ba-tab" aria-pressed="true" data-filter="">Todos</button>' + "".join(
        f'<button type="button" class="ba-tab" aria-pressed="false" data-filter="{escape(c)}">{escape(c)}</button>' for c in cats
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Blog do Dr. Fabiano",
        "url": f"{SITE}{path}",
        "publisher": ORG_REF,
        "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": f"{SITE}/blog/{p['slug']}/"} for p in POSTS],
    }
    page = head("Blog de Odontologia em Goiânia | Dr. Fabiano",
                "Guias sobre lentes de contato dental e implante dentário escritos pelo Dr. Fabiano, cirurgião-dentista em Goiânia: preços, cuidados, dúvidas e tratamentos.",
                path, "/images/casos/lentes-depois.webp", [schema, crumbs_schema])
    page += f"""
{HEADER}

<main id="conteudo">

<section class="page-hero page-hero-compact">
  <div class="hero-bg" aria-hidden="true"></div>
  <div class="container blog-hero">
    {crumbs_html}
    <p class="eyebrow">Guia do sorriso</p>
    <h1 class="page-title">Blog do Dr. Fabiano</h1>
    <p class="page-intro">Respostas claras para as dúvidas mais comuns sobre lentes de contato dental e implantes, escritas por quem atende em Goiânia há 30 anos.</p>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    <div class="blog-filters ba-tabs" role="group" aria-label="Filtrar artigos por tema">{filters}</div>
    <div class="post-grid" id="post-grid">
{chr(10).join(post_card(p) for p in POSTS)}
    </div>
  </div>
</section>

</main>
"""
    page += tail()
    return path, page


def blog_post(p):
    path = f"/blog/{p['slug']}/"
    crumbs_html, crumbs_schema = breadcrumb([("Início", "/"), ("Blog", "/blog/"), (p["h1"], path)])
    minutes = read_minutes(p["body"])
    cat_path, cat_name = CATEGORY_PAGE.get(p["category"], ("/#tratamentos", "Tratamentos"))
    related = [o for o in POSTS if o["category"] == p["category"] and o["slug"] != p["slug"]][:3]
    article_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["h1"],
        "description": p["description"],
        "image": f"{SITE}{p['image']}",
        "datePublished": p["date"],
        "dateModified": TODAY,
        "inLanguage": "pt-BR",
        "mainEntityOfPage": f"{SITE}{path}",
        "keywords": p["keyword"],
        "author": {"@type": "Person", "name": "Dr. Fabiano", "jobTitle": "Cirurgião-dentista", "url": f"{SITE}/#corpo-clinico"},
        "publisher": ORG_REF,
    }
    title = f"{p['title']} | Dr. Fabiano" if len(p["title"]) <= 48 else p["title"]
    page = head(escape(title), escape(p["description"]), path, p["image"], [article_schema, crumbs_schema, faq_schema(p["faqs"])])
    page += f"""
{HEADER}

<main id="conteudo">

<section class="page-hero page-hero-compact">
  <div class="hero-bg" aria-hidden="true"></div>
  <div class="container post-hero">
    {crumbs_html}
    <p class="eyebrow">{escape(p['category'])}</p>
    <h1 class="page-title">{escape(p['h1'])}</h1>
    <p class="post-meta"><span class="post-author">Por <strong>Dr. Fabiano</strong> · CRO-GO 00.000</span><span>{br_date(p['date'])}</span><span>{minutes} min de leitura</span></p>
  </div>
</section>

<div class="section section-white post-section">
  <div class="container article-grid">
    <article class="prose post-body">
      <figure class="post-cover"><img src="{p['image']}" alt="{escape(p['image_alt'])}" fetchpriority="high"></figure>
      {p['body']}
      <section class="post-faq">
        <h2>Perguntas frequentes</h2>
        <div class="faq-list">
{faq_html(p['faqs'])}
        </div>
      </section>
      <div class="post-cta">
        <p>Quer saber se este tratamento é indicado para você?</p>
        <div class="hero-ctas">
          <a class="btn btn-gold" data-wa="{escape(p['category'])} (vim pelo artigo do blog)" href="{WA}"><i class="ph-light ph-whatsapp-logo" aria-hidden="true"></i> Falar com a equipe</a>
          <a class="btn btn-ghost" href="{cat_path}">{cat_name} <i class="ph-light ph-arrow-right" aria-hidden="true"></i></a>
        </div>
      </div>
      <p class="post-disclaimer">Conteúdo informativo. Não substitui a avaliação clínica presencial. Resultados variam de pessoa para pessoa.</p>
    </article>
    {SIDE_CARD}
  </div>
</div>

<section class="section" aria-labelledby="relacionados">
  <div class="container">
    <header class="section-head reveal">
      <p class="eyebrow">Continue lendo</p>
      <h2 class="section-title" id="relacionados">Mais sobre {p['category'].lower()}</h2>
    </header>
    <div class="post-grid">
{chr(10).join(post_card(o) for o in related)}
    </div>
  </div>
</section>

</main>
"""
    page += tail()
    return path, page


def update_home_teaser():
    """Rewrites the blog teaser on the home page between the BLOG markers."""
    global index
    start, end = "<!-- BLOG:INICIO -->", "<!-- BLOG:FIM -->"
    if start not in index or not POSTS:
        return
    picks = []
    for cat in CATEGORY_PAGE:
        picks += [p for p in POSTS if p["category"] == cat][:2]
    picks = picks[:3]
    cards = "\n".join(post_card(p) for p in picks).replace('src="/images', 'src="images')
    block = f"""{start}
    <div class="post-grid">
{cards}
    </div>
    {end}"""
    index = re.sub(re.escape(start) + r".*?" + re.escape(end), block, index, flags=re.S)
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    print("atualizado bloco do blog na página inicial")


def write(path, html):
    out = ROOT / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("gerado", out.relative_to(ROOT))


pages = [treatment_page(t) for t in TREATMENTS] + [policy_page(p) for p in POLICIES]
if POSTS:
    pages += [blog_index()] + [blog_post(p) for p in POSTS]
for path, html in pages:
    write(path, html)
update_home_teaser()

urls = [("/", "1.0")] + [(f"/{t['slug']}/", "0.9") for t in TREATMENTS]
if POSTS:
    urls += [("/blog/", "0.7")] + [(f"/blog/{p['slug']}/", "0.7") for p in POSTS]
urls += [(f"/{p['slug']}/", "0.3") for p in POLICIES]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap += "".join(
    f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{prio}</priority>\n  </url>\n"
    for u, prio in urls
)
sitemap += "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
print("gerado sitemap.xml com", len(urls), "endereços")
