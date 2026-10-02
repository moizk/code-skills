---
paths:
  - "**/app/services/**/*.rb"
  - "**/app/queries/**/*.rb"
  - "**/app/forms/**/*.rb"
---

# Rails — services, queries, forms: one public method, Result objects, transactions

## Services
- **A service does one thing, named as a verb phrase with the `Service` suffix:** `CreateLeaseOfferService`, `Nooklyn::SyncLeasesService`.
- **Exactly one public method: `call`.** Everything else is private. A class-level `self.call(...)` that instantiates and delegates is fine as sugar.
- **Two public methods means two services**, or a different kind of object (query, builder, presenter). Split it.
- **The constructor takes keyword arguments and stores them in instance variables.** No `attr_reader` for them; they are private state.
- **Services don't know about HTTP.** No `params`, `session`, `flash`, `render`, or `current_user` inside. The controller passes plain values and the actor explicitly (`actor:`).
- **Services compose services.** A workflow with two steps calls two services and combines their Results; it never copies their bodies.

## Result object
- **Every service returns the project's shared Result**, never a boolean, nil, or a bare record. Reuse the existing type; introduce one shared type if none exists, never per-service shapes.
- **Callers branch on `success?` / `failure?`** and read the payload (`result.invoice`, `result.errors`). Never branch on the payload being nil.
- **Expected failures are failed Results; bugs raise.** Validation errors, declined cards, and conflicts return `failure`. A record that must exist but is missing raises and reaches the error tracker. Don't `rescue StandardError` into a failure.

```ruby
class Billing::CreateInvoiceService
  def self.call(**args) = new(**args).call

  def initialize(customer:, params:, actor:)
    @customer = customer
    @params = params
    @actor = actor
  end

  def call
    invoice = @customer.invoices.build(@params)
    return Result.failure(invoice: invoice) unless invoice.valid?

    ActiveRecord::Base.transaction do
      invoice.save!
      @customer.update!(last_invoiced_at: Time.current)
    end
    InvoiceMailer.with(invoice: invoice).created.deliver_later

    Result.success(invoice: invoice)
  end
end
```

## Transactions and side effects
- **Multi-record writes go in one `transaction` block** inside the service, using `save!` / `update!` so any failure rolls everything back.
- **Side effects run after the transaction commits.** Mail, jobs, webhooks, and external APIs sit below the `transaction` block, never inside it. A rolled-back transaction can't un-send an email.
- **Keep external calls out of transactions** for the same reason, and to keep locks short. Call out first, then write; or write, commit, then call out from a job.
- **Guard anything that can be retried or triggered twice** on state or a unique key before acting, so a double call doesn't double-charge.

## Query objects
- **A Query returns a Relation from `call`**, never an Array, so callers can paginate and compose further.
- **It takes its base relation as input** (`def initialize(relation = Invoice.all)`) so policy and tenant scopes can be applied before it.
- **Reads only.** A Query never writes, enqueues, or sends.

## Form objects
- **Use a Form when one submission validates or maps to more than one model.** It includes `ActiveModel::Model`, declares attributes and validations, and hands clean values to a service. It never saves.

Related: whether work runs inline or in a job is planned in `data-flow-plan`; jobs themselves follow `async-jobs`.
