---
paths:
  - "**/app/controllers/**/*.rb"
  - "**/app/policies/**/*.rb"
---

# Rails — controllers and policies: auth first, thin actions, strong params

## Auth first, every action
- **Every action authenticates, then authorizes, before any work.** A reader should see both at the top of the action or in `before_action`s it clearly inherits.
- **Authenticate the request** with the project's mechanism (Devise `authenticate_user!`, an OTP session, token auth). Never assume a signed-in user.
- **Authorize the specific action on the specific record** through the policy layer (`authorize @invoice`). Hidden UI and scoped finders are not authorization.
- **Load collections through the policy scope** (`policy_scope(Invoice)`) so what a user can list and what they can open always agree.

## Actions read as a script
- **Parse → authorize → call service → branch on result → respond.** Nothing else: no conditionals on domain state, no multi-model writes, no mail or jobs enqueued here.
- **One service call per action.** Two means the orchestration belongs inside a service.
- **Load the associations the view needs here** (`includes`, `preload`) or in the Query object. The view never triggers queries.

```ruby
def create
  authorize Invoice
  result = Billing::CreateInvoiceService.call(customer: current_customer, params: invoice_params, actor: current_user)

  if result.success?
    redirect_to result.invoice, notice: t('.created')
  else
    @invoice = result.invoice
    render :new, status: :unprocessable_entity
  end
end
```

## Strong parameters
- **One private method per action that takes input:** `invoice_params`, `invoice_update_params`. Use `params.expect` on Rails 8+ or `params.require(...).permit(...)` before that.
- **Never `permit!`, and never pass the raw `params` object into a service.** Hand it a permitted hash or explicit keyword arguments.
- **Permit nested attributes explicitly**, naming the `id` and `_destroy` keys.

## Errors and responses
- **Map domain errors once, in `ApplicationController`**, with `rescue_from AppError, with: :render_app_error`. Individual actions don't rescue.
- **Use the right status:** `:unprocessable_entity` when re-rendering a form after validation failure, `:not_found` for records the actor may not know exist (`:forbidden` leaks existence).
- **User-facing copy comes from locale files** (`t('.created')`), not string literals in the controller.

## Policies
- **One policy per model, one method per controller action** (`show?`, `update?`), plus a nested `Scope#resolve` for index queries.
- **Policies answer yes/no from the record and the actor only.** No database writes, no request params, no side effects.
- **Deny by default.** Don't inherit permissive defaults; an undefined policy method should raise, not allow.

## Filters
- **`before_action` is for loading and auth, not logic.** A filter that changes behavior based on domain state is hidden control flow.
- **Order filters so auth runs before anything loads**, and keep `only:` / `except:` lists explicit.

JSON endpoints follow the same rules plus the `rails-api` skill (status codes, error shape, pagination).
