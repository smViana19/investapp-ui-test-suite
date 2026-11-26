"""
US02 — Carteira (Portfolio.jsx)

Integrante 4: exclusão de ativos e métricas consolidadas.
- Exclusão de itens na tabela da carteira
- Tratamento do alerta nativo de confirmação (aceitar / cancelar)
- Recálculo imediato do card de Patrimônio Total
"""
import random
import re

import pytest
from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


ATIVO_PADRAO = "CDB"
QUANTIDADE = 10
PRECO_COMPRA = 100


def _prazo_unico():
    """Gera um par de prazos improvável de já existir na tabela, para isolar a linha do teste."""
    dias_inv = random.randint(101, 899)
    dias_plan = dias_inv + random.randint(30, 365)
    return dias_inv, dias_plan


@pytest.fixture
def carteira(logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage) -> PortfolioPage:
    """Usuário logado e posicionado na aba Carteira."""
    navbar.navegar_para_carteira()
    expect(portfolio_page.botao_adicionar).to_be_visible(timeout=10000)
    expect(portfolio_page.card_patrimonio_total).to_be_visible(timeout=10000)
    return portfolio_page


@pytest.fixture
def ativo_cadastrado(carteira: PortfolioPage):
    """Cadastra um aporte exclusivo para o teste e devolve seus dados."""
    dias_inv, dias_plan = _prazo_unico()
    carteira.cadastrar_aporte(ATIVO_PADRAO, QUANTIDADE, PRECO_COMPRA, dias_inv, dias_plan)

    linha = carteira.obter_linha_por_ativo_e_prazo(ATIVO_PADRAO, dias_inv, dias_plan)
    expect(linha).to_have_count(1, timeout=10000)

    return {"nome": ATIVO_PADRAO, "dias_inv": dias_inv, "dias_plan": dias_plan}


def test_exclusao_ativo_remove_linha_da_tabela(carteira: PortfolioPage, ativo_cadastrado: dict):
    """Ao confirmar a exclusão, a linha do ativo some e a tabela perde exatamente um item."""
    total_antes = carteira.total_de_ativos_listados()

    carteira.excluir_ativo_por_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"],
        confirmar=True,
    )

    linha = carteira.obter_linha_por_ativo_e_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"]
    )
    expect(linha).to_have_count(0, timeout=10000)
    expect(carteira.linhas_com_ativo).to_have_count(total_antes - 1)
    expect(carteira.alerta_erro).not_to_be_visible()


def test_exclusao_exibe_alerta_de_confirmacao(carteira: PortfolioPage, ativo_cadastrado: dict):
    """A exclusão deve passar por um alerta de confirmação antes de remover o ativo."""
    carteira.excluir_ativo_por_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"],
        confirmar=True,
    )

    linha = carteira.obter_linha_por_ativo_e_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"]
    )
    expect(linha).to_have_count(0, timeout=10000)

    assert carteira.ultima_mensagem_confirmacao, "Nenhum alerta de confirmação foi exibido na exclusão"


def test_cancelar_exclusao_mantem_ativo_e_patrimonio(carteira: PortfolioPage, ativo_cadastrado: dict):
    """Ao cancelar o alerta, o ativo permanece na tabela e o Patrimônio Total não muda."""
    total_antes = carteira.total_de_ativos_listados()
    patrimonio_antes = carteira.obter_texto_patrimonio_total()

    carteira.excluir_ativo_por_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"],
        confirmar=False,
    )

    linha = carteira.obter_linha_por_ativo_e_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"]
    )
    expect(linha).to_have_count(1)
    expect(carteira.linhas_com_ativo).to_have_count(total_antes)
    expect(carteira.card_patrimonio_total).to_have_text(patrimonio_antes)

    assert carteira.ultima_mensagem_confirmacao, "Nenhum alerta de confirmação foi exibido na exclusão"

    # Limpeza: remove o ativo criado para este teste
    carteira.excluir_ativo_por_prazo(
        ativo_cadastrado["nome"], ativo_cadastrado["dias_inv"], ativo_cadastrado["dias_plan"],
        confirmar=True,
    )
    expect(linha).to_have_count(0, timeout=10000)


def test_patrimonio_total_recalculado_imediatamente_apos_exclusao(carteira: PortfolioPage):
    """
    Cadastra um aporte, exclui em seguida e valida, sem recarregar a página,
    que o card de Patrimônio Total volta exatamente ao valor anterior ao aporte.
    """
    patrimonio_base_texto = carteira.obter_texto_patrimonio_total()
    patrimonio_base = carteira.obter_valor_patrimonio_total()

    dias_inv, dias_plan = _prazo_unico()
    carteira.cadastrar_aporte(ATIVO_PADRAO, QUANTIDADE, PRECO_COMPRA, dias_inv, dias_plan)
    linha = carteira.obter_linha_por_ativo_e_prazo(ATIVO_PADRAO, dias_inv, dias_plan)
    expect(linha).to_have_count(1, timeout=10000)

    # Com o aporte, o patrimônio precisa ter subido
    expect(carteira.card_patrimonio_total).not_to_have_text(patrimonio_base_texto, timeout=10000)
    patrimonio_com_aporte = carteira.obter_valor_patrimonio_total()
    assert patrimonio_com_aporte > patrimonio_base

    carteira.excluir_ativo_por_prazo(ATIVO_PADRAO, dias_inv, dias_plan, confirmar=True)
    expect(linha).to_have_count(0, timeout=10000)

    # Recálculo imediato: o card volta ao valor base sem reload
    expect(carteira.card_patrimonio_total).to_have_text(patrimonio_base_texto, timeout=10000)
    assert carteira.obter_valor_patrimonio_total() == pytest.approx(patrimonio_base, abs=0.01)
    assert carteira.obter_valor_patrimonio_total() < patrimonio_com_aporte


def test_excluir_todos_ativos_zera_patrimonio_total(carteira: PortfolioPage, ativo_cadastrado: dict):
    """Excluindo todos os ativos da carteira, o Patrimônio Total deve ficar zerado."""
    limite_exclusoes = 50
    restantes = carteira.total_de_ativos_listados()
    assert restantes > 0

    while restantes > 0 and limite_exclusoes > 0:
        patrimonio_antes = carteira.obter_texto_patrimonio_total()
        carteira.excluir_primeiro_ativo(confirmar=True)
        expect(carteira.linhas_com_ativo).to_have_count(restantes - 1, timeout=10000)

        # A cada exclusão o card precisa reagir (exceto se o item removido valia zero)
        if restantes - 1 > 0 and carteira.converter_moeda(patrimonio_antes) > 0:
            expect(carteira.card_patrimonio_total).not_to_have_text(patrimonio_antes, timeout=10000)

        restantes -= 1
        limite_exclusoes -= 1

    expect(carteira.linhas_com_ativo).to_have_count(0)
    expect(carteira.card_patrimonio_total).to_have_text(re.compile(r"^\D*0([.,]0+)?\s*$"), timeout=10000)
    assert carteira.obter_valor_patrimonio_total() == 0