# Tools and costs

Tool facts checked 9 October 2026. Public quotes are research snapshots, not the operator's invoices or connected account entitlements. Recheck before purchase/render; retain original currency, billing term, tax, exact job estimate and date.

## Minimal stack

| Job | Default | Escalation | Verification |
| --- | --- | --- | --- |
| Original reasoning and hooks | Existing assistant + Songcraft workflow | Specialist only when it adds useful review | Exact artifact and scope |
| Human/hybrid production | Owned DAW/session tools | Additional plugin, stems, score adapter | Actual compatibility and export |
| Generated audio | Authorized Suno account | Checked alternative provider | Visible mode/model, credits, export and terms |
| Cover | Native Suno or existing ChatGPT image workflow | Reusable art-direction workflow | Artwork export, rights and destination QA |
| Music film | Simple visualizer first | OpenArt Director OR Higgsfield scene workflow | Selected audio, job quote, coherent identity and final edit |
| Distribution | DistroKid appropriate primary-artist count | Alternative after rights/catalog needs review | Subscription, real receipt and exact profiles |
| Work/review | Notion | Existing private studio UI | Schema ownership and evidence pointer |
| Software | GitHub portable pack + private operated core | Hosting/worker only when needed | Source tests versus deployment receipts |
| Originals/evidence | Approved private asset archive | Durable object storage/backup | Hash, restore, access and retention |
| Reach | Existing YouTube + discovery + consented email | One authorized ad platform | Account access, tracking and spend receipts |

Do not subscribe to OpenArt and Higgsfield simultaneously for an unselected song. Compare the same 15–30 second excerpt after selection, with authorized attempts, then fund one provider for that campaign.

## Provider evidence

- Suno pricing displays Pro USD 8/month and Premier USD 24/month under annual billing (USD 96 / USD 288 annualized before checkout tax). Included monthly credits are 2,500 / 10,000 and ordinary song downloads 20 / 60. These are not month-to-month EUR quotes. Studio's documented download exception is a separate workflow. https://suno.com/pricing and https://help.suno.com/en/articles/13614785
- Native cover-image editing is documented; cover art is separate from the audio Cover feature. Album artwork reuse in Suno does not establish DSP artwork compliance. https://suno.com/release-notes/cover-art-improvements and https://help.suno.com/en/articles/14227585
- OpenArt Director documents uploading an existing track and directing a full music video. Public pricing contains billing toggles/promotions and excludes Director from headline approximate video counts; per-song Director cost remains a job-quote dependency. https://openart.ai/features/ai-music-video-generator/ and https://openart.ai/pricing
- Higgsfield documents identity references, generated scenes, lip sync and final editing. Its pricing page did not expose reliable plan numbers in the retrieved text; budget from an actual in-account quote. This is a controlled scene workflow, not proof of a connected one-click full-video adapter. https://higgsfield.ai/blog/ai-music-video-real-artist-2026 and https://higgsfield.ai/pricing
- DistroKid's public Musician Plus quote is USD 44.99/year for two artists; Ultimate starts at USD 89.99/year for five-plus artists. Future release dates and a customizable label name are listed on Plus/Ultimate. Extras, taxes and additional artists require checkout review. https://distrokid.com/product/distrokid/plans-and-pricing-2

An artist name is not a Suno account. Additional accounts/subscriptions need a real creative, ownership or access reason; persona count alone is insufficient.

## Proposed campaign allowances (EUR, not vendor prices)

| Category | Lean | Standard | Flagship |
| --- | ---: | ---: | ---: |
| Allocated subscriptions/storage | 40 | 60 | 100 |
| Music production/edit/export | 30 | 60 | 120 |
| Cover/video derivatives | 20 | 100 | 300 |
| Distribution extras/delivery | 10 | 15 | 30 |
| Marketing experiments | 60 | 160 | 400 |
| Agent/model reasoning | 15 | 35 | 70 |
| Contingency reserve | 25 | 70 | 180 |
| Total envelope | 200 | 500 | 1,200 |

These are planning options only. Existing subscriptions can reduce incremental cash; do not confuse allocated economic cost with new cash. Charge an invoice once: shared subscription allocation is analytical and must not also be counted as another purchase in the campaign cash ledger.

Production attempts, usable exports and download quotas are separately bounded. Native quotas may make downloads the constraint before generation credits. Planned credits, observed balances, pending reservations and real spend remain distinct; an unobserved balance blocks execution readiness.

Cash ledger: stable line ID, campaign, category, plan allowance, actual cash (null until reconciled), resource quantity, invoice/receipt, currency, conversion basis, allocation rule and authorization pointer. Marketing experiment caps sit inside the marketing allowance; never add them to it again. Royalties use actual statements and lagged windows, not a fixed payout-per-stream promise.

## Offline planner

Run from the checkout or exported pack:

```bash
python scripts/campaign_cli.py report docs/business-os/campaign.example.json
python scripts/campaign_cli.py build-pack /absolute/new/path/music-producer-os-draft.zip
```

The report sums allowances, preserves unknown actual costs, checks independent credit/download balances and experiment allocations, and proposes dates only if supplied. It never grants execution, rights or publication permission and makes no network call.

## EUR 99 customer-pack economics

Price is an untested hypothesis, not an active listing. For illustration only: at EUR 99 VAT-inclusive and an assumed 21% VAT treatment, revenue excluding VAT is EUR 81.82. If payment costs were EUR 4, refund reserve EUR 4, fulfillment EUR 1 and support ten minutes at EUR 60/hour (EUR 10), contribution before acquisition would be EUR 62.82. These inputs are assumptions; actual merchant, tax treatment, channel fees, refund rate and customer acquisition cost remain unknown.

Notion Marketplace currently documents an 8% plus USD 0.40 transaction fee, USD sales, regional tax handling as merchant of record and an extra 1% FX fee for non-US creator payouts. Do not reuse the EUR illustration as a Marketplace payout model. https://www.notion.com/help/selling-on-marketplace

A one-time pack must work without bespoke setup. Paid tool credits, hosted compute, advertisement spend, commercial music licenses and managed account execution are outside its price. Any recurring edition must have separate ongoing delivered value and cost evidence.

