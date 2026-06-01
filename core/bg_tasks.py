import asyncio


async def recalculate_advanced_metrics(match_id: int):
    await asyncio.sleep(3)
    print(f"Métricas avançadas da partida {match_id} recalculadas com sucesso.")
