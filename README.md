# The Perspectives — News Website

Bilingual news platform (English / Kinyarwanda) with **language in the URL**.

---

## URL Structure

```
/              → redirects to /en/
/en/           → English homepage
/rw/           → Kinyarwanda homepage

/en/category/<slug>/                    → main category listing
/en/subcategory/<slug>/                 → sub-category listing (ALL articles with this topic)
/en/category/<cat>/sub/<sub>/           → main category filtered by topic
/en/article/<slug>/                     → full article
/en/search/?q=...                       → search (English only)

/rw/category/u-rwanda/                  → Kinyarwanda category
/rw/subcategory/politiki/               → Kinyarwanda sub-category
/rw/search/?q=...                       → search (Kinyarwanda only)
```

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Migrate
python manage.py migrate

# 3. Create languages, categories, sub-categories, superuser
python manage.py setup_site

# 4. Run
python manage.py runserver
```

- English:    http://127.0.0.1:8000/en/
- Kinyarwanda: http://127.0.0.1:8000/rw/
- Admin:      http://127.0.0.1:8000/admin/   →  admin / admin123

---

## Key Design Decisions

### Language in URL
Language is determined purely from the URL prefix `/en/` or `/rw/`.
No sessions, no cookies, no Django i18n middleware needed.
Language switch = redirect to the same page with the other language prefix.

### Sub-categories are INDEPENDENT
Sub-categories are NOT children of main categories.
The same 10 topics (Politics, Economy, …) exist in every main category.

**Model structure:**
```
Language
  ├── MainCategory  (Rwanda / Africa / World / Research Paper)
  └── SubCategory   (Politics / Economy / … / Trends)   ← NO FK to MainCategory

Article
  ├── language      FK → Language
  ├── main_category FK → MainCategory  (which big bucket)
  └── sub_category  FK → SubCategory   (which topic)
```

**Result:**
- `/en/subcategory/politics/`  → ALL politics articles (Rwanda + Africa + World + Research)
- `/en/category/rwanda/sub/politics/`  → Rwanda + Politics combined filter
- `/rw/subcategory/politiki/`  → ALL Politiki articles in Kinyarwanda

### Language Switcher
The switcher POSTs to `/switch-lang/` with `lang=en|rw` and `next=<current_path>`.
The view swaps the language prefix in the path and redirects.
No Django i18n sessions — just URL manipulation.

---

## Categories

### English
| Main Category  | Slug            |
|----------------|-----------------|
| Rwanda         | rwanda          |
| Africa         | africa          |
| World          | world           |
| Research Paper | research-paper  |

### Kinyarwanda
| Main Category                | Slug            |
|------------------------------|-----------------|
| U Rwanda                     | u-rwanda        |
| Afurika                      | afurika         |
| Isi                          | isi             |
| Inyandiko z'Ubushakashatsi   | ubushakashatsi  |

### Sub-categories (same 10 per language, independent of main cat)
| English        | Kinyarwanda                  |
|----------------|------------------------------|
| Politics       | Politiki                     |
| Economy        | Ubukungu                     |
| Education      | Uburezi                      |
| Society        | Sosiyete                     |
| Culture & Arts | Umuco & Ubugeni              |
| Science & Tech | Ubumenyi & Ikoranabuhanga    |
| Religion       | Iyobokamana                  |
| Environment    | Ibidukikije                  |
| Health         | Ubuzima                      |
| Trends         | Ibigezweho                   |

---

## Adding Articles in Admin

1. Go to `/admin/` → Articles → Add Article
2. **Select Language** (EN or RW) — determines which category list appears
3. Select **Main Category** (Rwanda / Africa / World / Research Paper)
4. Select **Sub Category** (Politics / Economy / … — independent list)
5. Write Title, Summary, Content (Summernote rich editor)
6. Upload Featured Image
7. Set **Published At** datetime and **Status = Published**
8. Tick **Is Featured / Trending / Breaking** as needed

> For bilingual coverage of the same story: create **two Article records**,
> one with Language=English, one with Language=Kinyarwanda.

---

## Features
- ✅ Language in URL — /en/ and /rw/
- ✅ Language switcher in top bar (swaps URL prefix)
- ✅ Sub-categories fully independent — browse across all main categories
- ✅ Combined filter: category + sub-category
- ✅ Breaking news ticker
- ✅ Featured hero section + side items
- ✅ Trending sidebar
- ✅ Per-category article blocks on homepage
- ✅ Full article: breadcrumb, author, date/time, main cat, sub cat, share, comments, related, trending sidebar
- ✅ Search scoped to active language only
- ✅ Summernote rich text editor in admin
- ✅ Responsive Bootstrap 4
- ✅ Brand colours from The Perspectives logo (Navy #1B3A8C, Gold #F5C400, Green #2D7A3A)

---

## Brand Colours
| Name       | Hex       | Usage                                  |
|------------|-----------|----------------------------------------|
| Navy       | `#1B3A8C` | Navbar, headings, primary UI           |
| Dark Navy  | `#122968` | Navbar background                      |
| Gold       | `#F5C400` | Accents, hover states, highlights      |
| Green      | `#2D7A3A` | Secondary badges                       |
| Dark Grey  | `#3A3A3A` | Body text                              |
