"""
LOGGING MIGRATION TEMPLATE

This file shows the pattern to apply when migrating any module to use 
the new modular logging system.

Copy this template and adapt it for your specific module.
"""

# ============================================================================
# TEMPLATE 1: Basic Module Template
# ============================================================================

"""
Your module description here.

Example:
    This module handles document ingestion and processing.
"""

# STEP 1: Import the new LoggerManager
from ..logger_config_enhanced import LoggerManager

# STEP 2: Create logger with correct module name
# Choose from: document_ingestion, vector_store, llm_queries, api_endpoints, 
#              rag_engine, dataset, frontend, opik_tracing, error, debug
logger = LoggerManager.get_logger(__name__, "document_ingestion")


# STEP 3: Use logger throughout your module
class YourService:
    """Your service class."""
    
    def your_method(self):
        """Your method with proper logging."""
        logger.info("Starting operation")
        
        try:
            # Do your work
            logger.info("Operation completed successfully")
        except Exception as e:
            logger.error("Operation failed", exc_info=True)
            raise


# ============================================================================
# TEMPLATE 2: With Timing
# ============================================================================

import time

logger = LoggerManager.get_logger(__name__, "vector_store")


class FAISSService:
    """Vector store operations."""
    
    def index_documents(self, documents):
        """Add documents to index with timing."""
        logger.info(f"Indexing {len(documents)} documents")
        
        start_time = time.time()
        try:
            # Index documents
            for doc in documents:
                self._index_single(doc)
            
            elapsed = time.time() - start_time
            logger.info(
                f"Indexing completed | "
                f"Count: {len(documents)} | "
                f"Time: {elapsed:.2f}s | "
                f"Speed: {len(documents) / elapsed:.1f} docs/sec"
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Indexing failed | Time: {elapsed:.2f}s", 
                exc_info=True
            )
            raise


# ============================================================================
# TEMPLATE 3: With Context and Metrics
# ============================================================================

logger = LoggerManager.get_logger(__name__, "llm_queries")


class LLMEngine:
    """LLM query handling."""
    
    async def generate(self, prompt, **kwargs):
        """Generate response with comprehensive logging."""
        input_tokens = len(prompt.split())
        
        logger.info(
            f"LLM Query Started | "
            f"Model: {self.model} | "
            f"Input tokens (~): {input_tokens} | "
            f"Temperature: {self.temperature}"
        )
        
        start_time = time.time()
        try:
            # Call LLM
            response = await self.api_call(prompt, **kwargs)
            
            latency = time.time() - start_time
            cost = self._estimate_cost(response.usage)
            
            logger.info(
                f"LLM Query Completed | "
                f"Latency: {latency:.2f}s | "
                f"Input tokens: {response.usage.prompt_tokens} | "
                f"Output tokens: {response.usage.completion_tokens} | "
                f"Total tokens: {response.usage.total_tokens} | "
                f"Estimated cost: ${cost:.6f}"
            )
            
            return response
            
        except Exception as e:
            latency = time.time() - start_time
            logger.error(
                f"LLM Query Failed | "
                f"Model: {self.model} | "
                f"Latency: {latency:.2f}s",
                exc_info=True
            )
            raise


# ============================================================================
# TEMPLATE 4: With Error Handler
# ============================================================================

logger = LoggerManager.get_logger(__name__, "api_endpoints")


class APIEndpoint:
    """FastAPI endpoint with error handling."""
    
    async def process_request(self, request):
        """Process request with comprehensive logging."""
        logger.info(f"Request received | Path: {request.url.path}")
        
        start_time = time.time()
        try:
            result = await self._do_work(request)
            
            elapsed = time.time() - start_time
            logger.info(
                f"Request successful | "
                f"Status: 200 | "
                f"Time: {elapsed:.2f}s"
            )
            return result
            
        except ValueError as e:
            elapsed = time.time() - start_time
            logger.warning(
                f"Request validation failed | "
                f"Time: {elapsed:.2f}s | "
                f"Error: {str(e)}"
            )
            raise
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Request failed | "
                f"Time: {elapsed:.2f}s",
                exc_info=True
            )
            raise


# ============================================================================
# TEMPLATE 5: Multi-Component Service
# ============================================================================

from ..logger_config_enhanced import LoggerManager

# Get loggers for different components this service uses
main_logger = LoggerManager.get_logger(__name__, "rag_engine")
doc_logger = LoggerManager.get_logger(__name__, "document_ingestion")
vector_logger = LoggerManager.get_logger(__name__, "vector_store")
llm_logger = LoggerManager.get_logger(__name__, "llm_queries")


class RAGEngine:
    """RAG pipeline with multi-component logging."""
    
    def answer_question(self, question):
        """Answer question using RAG pipeline."""
        main_logger.info(f"RAG pipeline started | Question: {question[:60]}...")
        
        total_start = time.time()
        
        try:
            # Step 1: Embed question
            main_logger.info("Step 1: Embedding question")
            embed_start = time.time()
            embedding = self.embedder.embed(question)
            embed_time = time.time() - embed_start
            main_logger.info(f"Question embedded | Time: {embed_time*1000:.1f}ms")
            
            # Step 2: Retrieve documents
            main_logger.info("Step 2: Retrieving relevant documents")
            vector_logger.info(f"Searching for top-5 documents")
            retrieve_start = time.time()
            docs = self.vector_store.search(embedding, k=5)
            retrieve_time = time.time() - retrieve_start
            vector_logger.info(f"Search completed | Results: {len(docs)} | Time: {retrieve_time*1000:.1f}ms")
            main_logger.info(f"Documents retrieved | Count: {len(docs)} | Time: {retrieve_time*1000:.1f}ms")
            
            # Step 3: Generate answer
            main_logger.info("Step 3: Generating answer with LLM")
            llm_logger.info(f"Calling LLM with {len(docs)} documents")
            gen_start = time.time()
            answer = self.llm.generate(self._build_prompt(question, docs))
            gen_time = time.time() - gen_start
            llm_logger.info(f"LLM generated response | Time: {gen_time:.2f}s")
            main_logger.info(f"Answer generated | Length: {len(answer)} chars")
            
            # Summary
            total_time = time.time() - total_start
            main_logger.info(
                f"RAG pipeline completed | "
                f"Total time: {total_time:.2f}s | "
                f"Breakdown: Embed({embed_time*1000:.0f}ms) + "
                f"Retrieve({retrieve_time*1000:.0f}ms) + "
                f"Generate({gen_time*1000:.0f}ms)"
            )
            
            return answer
            
        except Exception as e:
            total_time = time.time() - total_start
            main_logger.error(
                f"RAG pipeline failed | "
                f"Total time: {total_time:.2f}s | "
                f"Question: {question[:60]}...",
                exc_info=True
            )
            raise


# ============================================================================
# TEMPLATE 6: Data Processing with Batch Logging
# ============================================================================

logger = LoggerManager.get_logger(__name__, "document_ingestion")


class DocumentProcessor:
    """Process multiple documents with progress logging."""
    
    def process_batch(self, documents):
        """Process batch of documents with progress."""
        total = len(documents)
        logger.info(f"Starting batch processing | Total: {total} documents")
        
        start_time = time.time()
        succeeded = 0
        failed = 0
        
        try:
            for i, doc in enumerate(documents):
                try:
                    # Process single document
                    result = self._process_single(doc)
                    succeeded += 1
                    
                    # Progress logging every 10 items
                    if (i + 1) % 10 == 0:
                        elapsed = time.time() - start_time
                        rate = (i + 1) / elapsed
                        logger.info(
                            f"Progress | "
                            f"Completed: {i+1}/{total} | "
                            f"Rate: {rate:.1f} docs/sec | "
                            f"Succeeded: {succeeded} | "
                            f"Failed: {failed}"
                        )
                
                except Exception as e:
                    failed += 1
                    logger.warning(
                        f"Document processing failed | "
                        f"Document: {doc.name} | "
                        f"Error: {str(e)}"
                    )
            
            # Final summary
            total_time = time.time() - start_time
            logger.info(
                f"Batch processing completed | "
                f"Total: {total} | "
                f"Succeeded: {succeeded} | "
                f"Failed: {failed} | "
                f"Success rate: {(succeeded/total)*100:.1f}% | "
                f"Time: {total_time:.2f}s | "
                f"Rate: {total/total_time:.1f} docs/sec"
            )
            
            return succeeded, failed
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(
                f"Batch processing failed | "
                f"Processed: {i+1}/{total} | "
                f"Time: {total_time:.2f}s",
                exc_info=True
            )
            raise


# ============================================================================
# TEMPLATE 7: Database Operations
# ============================================================================

logger = LoggerManager.get_logger(__name__, "dataset")


class DatasetService:
    """Dataset management with detailed logging."""
    
    def create_dataset(self, dataset_id, name, description):
        """Create new dataset."""
        logger.info(
            f"Creating dataset | "
            f"ID: {dataset_id} | "
            f"Name: {name}"
        )
        
        try:
            # Create dataset
            dataset = self._db.create_dataset(
                id=dataset_id,
                name=name,
                description=description
            )
            
            logger.info(
                f"Dataset created successfully | "
                f"ID: {dataset_id} | "
                f"DB ID: {dataset.db_id}"
            )
            
            return dataset
            
        except Exception as e:
            logger.error(
                f"Failed to create dataset | "
                f"ID: {dataset_id} | "
                f"Name: {name}",
                exc_info=True
            )
            raise
    
    def add_test_case(self, dataset_id, test_case):
        """Add test case to dataset."""
        logger.info(
            f"Adding test case | "
            f"Dataset: {dataset_id} | "
            f"Input: {test_case.input[:50]}..."
        )
        
        try:
            result = self._db.add_test_case(dataset_id, test_case)
            
            logger.info(
                f"Test case added | "
                f"Dataset: {dataset_id} | "
                f"Case ID: {result.id}"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Failed to add test case | "
                f"Dataset: {dataset_id}",
                exc_info=True
            )
            raise


# ============================================================================
# MIGRATION CHECKLIST
# ============================================================================

"""
When migrating a module, use this checklist:

BEFORE CODING:
- [ ] Decide which module category this fits into (see LOGGING_QUICK_REFERENCE.md)
- [ ] Identify all classes and methods that should log
- [ ] Plan what information is important to log

CODING:
- [ ] Import LoggerManager from logger_config_enhanced
- [ ] Create logger with correct module name
- [ ] Add info logs at method entry points
- [ ] Add timing logs for performance-critical operations
- [ ] Add error logs with exc_info=True
- [ ] Add context (file names, IDs, counts, etc.) to all logs

TESTING:
- [ ] Run the module as normal
- [ ] Verify logs appear in correct file (tail -f logs/components/module_name.log)
- [ ] Verify error logs appear in errors.log (tail logs/errors.log)
- [ ] Verify log format is consistent
- [ ] Verify no sensitive data is logged

VALIDATION:
- [ ] Check disk space: du -h logs/
- [ ] Check log file permissions: ls -la logs/components/
- [ ] Run with DEBUG level: LOG_LEVEL=DEBUG python ...
- [ ] Test error scenarios: Verify error logs have traceback

DOCUMENTATION:
- [ ] Update module docstring if logging behavior changed
- [ ] Add example to LOGGING_MIGRATION_EXAMPLES.md
- [ ] Update README if needed
"""

# ============================================================================
# FREQUENTLY USED PATTERNS
# ============================================================================

"""
1. SIMPLE INFO LOG
   logger.info("Operation completed")

2. WITH PARAMETERS
   logger.info(f"Processing | File: {filename} | Size: {size}MB")

3. WITH TIMING
   start = time.time()
   # do work
   logger.info(f"Completed | Time: {time.time()-start:.2f}s")

4. WITH ERROR
   try:
       # do work
   except Exception as e:
       logger.error("Failed to process", exc_info=True)

5. WITH CONTEXT AND MULTIPLE FIELDS
   logger.info(
       f"Operation | "
       f"Param1: {p1} | "
       f"Param2: {p2} | "
       f"Time: {elapsed:.2f}s | "
       f"Result: {result_count} items"
   )

6. PROGRESS TRACKING (EVERY N ITEMS)
   for i in range(total):
       if (i + 1) % 100 == 0:
           logger.info(f"Progress | Completed: {i+1}/{total}")

7. CONDITIONAL LOGGING (ONLY ERRORS)
   if not result.success:
       logger.warning(f"Operation failed | Reason: {result.error}")

8. BATCH OPERATION SUMMARY
   logger.info(
       f"Batch completed | "
       f"Total: {total} | "
       f"Success: {success} | "
       f"Failed: {failed} | "
       f"Rate: {rate:.1f}/sec"
   )
"""
