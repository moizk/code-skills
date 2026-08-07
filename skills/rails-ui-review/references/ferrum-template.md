# Ferrum screenshot template (pure Ruby; adapt per review)

Run with `RAILS_ENV=test bin/rails runner ui_review.rb` (Ferrum is bundled when
the app drives system specs with Cuprite) or plain `ruby` with `BASE`/`PORT` in
the env. Saves PNGs to `tmp/ui_review/` for you to read — the Read tool renders
images.

Mirror the app's own system-spec driver config (often `spec/support/cuprite.rb`)
for Chrome flags — but size the window yourself: **the wide pass must be
≥1680px** (a mid width like 1400 hides shrink-wrap, centering, and
overlay-clipping bugs), and a narrow pass checks responsive behavior.

```ruby
require "ferrum"; require "fileutils"
BASE = ENV.fetch("BASE", "http://127.0.0.1:#{ENV.fetch('PORT')}")
OUT  = "tmp/ui_review"; FileUtils.mkdir_p(OUT)
# wide first: >=1680 is where shrink-wrap / centering / clipping bugs live
b = Ferrum::Browser.new(headless: true, window_size: [1680, 1200],
                        browser_options: { "no-sandbox": nil }, process_timeout: 20)
def shot(b, name, full: true) b.screenshot(path: "tmp/ui_review/#{name}.png", full: full); puts "shot #{name}" end

# scroll the full height so lazy-loaded content + sticky/footer elements render, then back to top
def scroll_through(b)
  b.execute("window.scrollTo(0, document.body.scrollHeight)"); b.network.wait_for_idle rescue nil
  b.execute("window.scrollTo(0, 0)")
end
# click each match (modals, dropdowns, accordions, tabs), shoot the opened state, then close with Esc
def open_each(b, name, selector)
  b.css(selector).first(6).each_with_index do |el, i|
    (el.click rescue next); b.network.wait_for_idle rescue nil
    shot(b, "#{name}-open-#{i}"); b.keyboard.type(:Escape) rescue nil
  end
end
# hover each match (tooltips/popovers) and shoot the revealed state
def hover_each(b, name, selector)
  b.css(selector).first(6).each_with_index { |el, i| (el.hover rescue next); shot(b, "#{name}-tip-#{i}") }
end

# --- log in via the app's form (skip for public pages; adapt path + field names) ---
b.goto("#{BASE}/users/sign_in")
b.at_css('input[name="user[email]"]').focus.type(ENV.fetch("EMAIL", "ui-admin@example.test"))
b.at_css('input[name="user[password]"]').focus.type(ENV.fetch("PASSWORD", "password123"))
b.at_css('form input[type="submit"], form button[type="submit"]').click
b.network.wait_for_idle rescue nil

# --- visit the pages under review (edit this list) ---
{ "index" => "/things",
  "new"   => "/things/new" }.each do |name, path|
  b.goto("#{BASE}#{path}")
  b.network.wait_for_idle rescue nil
  shot(b, name)
  scroll_through(b); shot(b, "#{name}-bottom")
  # reveal interactive content — ADAPT these selectors to the app's markup (Bootstrap/Stimulus/headless/etc.)
  open_each(b,  name, "[data-bs-toggle='modal'], [data-toggle='modal'], [aria-haspopup='dialog'], dialog ~ [data-action*='modal']")
  open_each(b,  name, ".dropdown-toggle, [data-bs-toggle='dropdown'], [aria-haspopup='menu'], details > summary")
  hover_each(b, name, "[data-bs-toggle='tooltip'], [data-toggle='tooltip'], [aria-describedby], [title]")
  errs = b.evaluate("window.__jsErrors || []") rescue []
  warn "JS errors on #{name}: #{errs}" if errs && !errs.empty?
end

# --- a narrow viewport to check responsive ---
b.resize(width: 480, height: 1000); b.goto("#{BASE}/things")
b.network.wait_for_idle rescue nil; shot(b, "index-mobile")
b.quit
```

Then **read** `tmp/ui_review/*.png` and assess — including the `-bottom`,
`-open-*`, and `-tip-*` shots, so deferred and interactive content is actually
reviewed. The `open_each`/`hover_each`/`scroll_through` helpers surface modals,
dropdowns, tooltips, and below-the-fold content; **tune their selectors to the
app's own markup** (use `b.evaluate("...")` to toggle a view or trigger a state
before a shot).
