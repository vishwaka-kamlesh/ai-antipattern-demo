rules:

  # 1. Empty catch blocks - FIXED with better pattern
  - id: empty-catch-block
    languages: [java]
    severity: ERROR
    message: Empty catch block swallows exceptions. At minimum log or rethrow.
    pattern: |
      catch (...) {
      }

  # 11a. N+1 query - repository calls in loop
  - id: nplus1-query-repository
    languages: [java]
    severity: ERROR
    message: Potential N+1 query - repository call inside loop. Use JOIN FETCH, @EntityGraph, or batch fetching.
    patterns:
      - pattern: |
          for ($E : $LIST) {
            ...
            $REPO.$METHOD(...);
            ...
          }
      - metavariable-regex:
          metavariable: $REPO
          regex: .*(Repository|Repo|repository|repo)

  # 11b. N+1 query - entity getter calls (lazy loading)
  - id: nplus1-query-lazy-loading
    languages: [java]
    severity: ERROR
    message: Potential N+1 query - lazy loading inside loop. Use JOIN FETCH or @EntityGraph to fetch eagerly.
    patterns:
      - pattern: |
          for ($ITEM : $ITEMS) {
            ...
            $ITEM.get$METHOD(...);
            ...
          }
      - metavariable-regex:
          metavariable: $METHOD
          regex: (Orders|Users|Payments|Invoices|Customer|Product|Items|Details|Address|Profile)

  # 23a. Remove from collection while iterating
  - id: modify-collection-while-iterating-remove
    languages: [java]
    severity: ERROR
    message: Removing from collection during iteration causes ConcurrentModificationException. Use Iterator.remove() instead.
    pattern: |
      for ($ITEM : $COLL) {
        ...
        $COLL.remove(...);
        ...
      }

  # 23b. Add to collection while iterating
  - id: modify-collection-while-iterating-add
    languages: [java]
    severity: ERROR
    message: Adding to collection during iteration causes ConcurrentModificationException. Collect to new collection instead.
    pattern: |
      for ($ITEM : $COLL) {
        ...
        $COLL.add(...);
        ...
      }