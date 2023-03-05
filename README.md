# lens-discovery-hackathon

Recommendation engine for Lens protocol, implemented with vector search and built on top of Cartesi rollup

## Architecture

### This is what we planned for

```mermaid
sequenceDiagram
    autonumber

    #participant Web App
    #participant Cartesi Rollup
    #participant Cartesi Machine
    #participant Vector DB
    #participant Worker
    

    Worker ->> Lens API: getContent()
    Lens API -->> Worker: (content)
    
    Worker ->> Vector DB: upsert(content)
    
    Web App ->> Cartesi Rollup: submitQuery(query)
    Cartesi Rollup -->> Web App: (txHash)
    
    Note right of Cartesi Rollup: Process tx
    
    Cartesi Machine ->> Cartesi Rollup: getRequest()
    Cartesi Rollup -->> Cartesi Machine: (query)
    
    Cartesi Machine ->> Cartesi Machine: tokens = tokenize(query)
    Cartesi Machine ->> Vector DB: search(tokens)
    Vector DB -->> Cartesi Machine: (results)
    Cartesi Machine ->> Cartesi Rollup: submitOutputs(results)
    
    Web App ->> Cartesi Rollup: queryOutputs()
    Cartesi Rollup -->> Web App: (searchResults)
```

### This is what we got

```mermaid
sequenceDiagram
    autonumber

    #participant Web App
    #participant Cartesi Rollup
    #participant Backend
    #participant Vector DB
    #participant Worker
    

    Worker ->> Lens API: getContent()
    Lens API -->> Worker: (content)
    
    Worker ->> Vector DB: upsert(content)
    
    Web App ->> Backend: submitQuery(query)
    Backend ->> Backend: tokens = tokenize(query)
    Backend ->> Vector DB: search(tokens)
    Backend -->> Web App: (searchResults)
```
