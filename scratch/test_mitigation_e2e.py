import asyncio
from backend.api.routes import get_rag_service

async def main():
    service = get_rag_service()
    
    query = "college admission-ku eligibility என்ன?"
    
    print("=== TEST 1: MITIGATION OFF ===")
    res_off = service.answer_query(query, mitigation_enabled=False)
    print(f"Mitigation Applied: {res_off.mitigation_applied}")
    print(f"Normalized Query: {res_off.normalized_query}")
    print(f"Answer: {res_off.answer[:100]}...\n")
    
    print("=== TEST 2: MITIGATION ON ===")
    res_on = service.answer_query(query, mitigation_enabled=True)
    print(f"Mitigation Applied: {res_on.mitigation_applied}")
    print(f"Normalized Query: {res_on.normalized_query}")
    print(f"Answer: {res_on.answer[:100]}...\n")

if __name__ == "__main__":
    asyncio.run(main())
