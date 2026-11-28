import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage
from pages.yield_simulator_page import YieldSimulatorPage


def test_aba_simulador_carrega(logged_page: Page, navbar: NavbarComponent, yield_page: YieldSimulatorPage):
    """Valida que a aba do Simulador abre com os controles de projeção visíveis."""
    navbar.navegar_para_simulador()

    expect(yield_page.titulo_aba).to_be_visible()
    expect(yield_page.input_meses).to_be_visible()
    expect(yield_page.botao_simular).to_be_visible()


@pytest.mark.parametrize("meses", [1, 6, 12, 24, 60])
def test_tabela_renderiza_quantidade_de_meses(
    logged_page: Page, navbar: NavbarComponent, yield_page: YieldSimulatorPage, meses: int
):
    """Ajusta o campo e valida que a tabela exibe exatamente N linhas de mês (1 a 60)."""
    navbar.navegar_para_simulador()

    yield_page.simular_projecao(meses)

    expect(yield_page.titulo_resultado).to_be_visible(timeout=8000)
    expect(yield_page.linhas_meses).to_have_count(meses, timeout=8000)
    expect(yield_page.obter_linha_do_mes(meses)).to_be_visible()


def test_ajuste_do_campo_mantem_valor(
    logged_page: Page, navbar: NavbarComponent, yield_page: YieldSimulatorPage
):
    """Valida que o controle de meses mantém o valor informado."""
    navbar.navegar_para_simulador()

    yield_page.definir_meses(36)

    expect(yield_page.input_meses).to_have_value("36")


def test_tabela_discriminada_por_tipo_de_ativo(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
    yield_page: YieldSimulatorPage,
):
    """Cadastra um aporte e valida que a tabela discrimina o ativo e mostra o total."""
    navbar.navegar_para_carteira()
    portfolio_page.cadastrar_aporte(
        ativo="Poupança", quantidade="1000.00", preco="1.00", dias_inv="0", dias_plan="365"
    )
    expect(portfolio_page.obter_linha_por_ativo_e_prazo("Poupança", "0", "365")).to_be_visible(timeout=5000)

    navbar.navegar_para_simulador()
    yield_page.simular_projecao(12)

    expect(yield_page.tabela_rendimento).to_be_visible(timeout=8000)
    expect(yield_page.obter_coluna_ativo("Poupança")).to_be_visible()
    expect(yield_page.coluna_total).to_be_visible()