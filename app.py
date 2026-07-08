import streamlit as st
import openpyxl
from pypdf import PdfReader
from google import genai
import os

# Configuração da página do site
st.set_page_config(page_title="Sistema de Inspeção Inteligente", page_icon="⚙️", layout="centered")

st.title("⚙️ Sistema de Inspeção de Qualidade")
st.markdown("Faça o upload do desenho técnico e do modelo em Excel para preencher o relatório automaticamente via IA.")

# O Streamlit busca a chave da API automaticamente das variáveis de ambiente do sistema
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Chave da API do Gemini não encontrada! Verifique as configurações do sistema.")
else:
    # Interface para upload de arquivos
    desenho_file = st.file_uploader("1. Selecione o Desenho Técnico (PDF)", type=["pdf"])
    modelo_file = st.file_uploader("2. Selecione o Modelo do Relatório (XLSX)", type=["xlsx"])

    if desenho_file and modelo_file:
        if st.button("🚀 Processar e Preencher Relatório", use_container_width=True):
            with st.spinner("A inteligência artificial está analisando o desenho técnico rigorosamente..."):
                try:
                    # 1. Ler as informações do PDF
                    leitor = PdfReader(desenho_file)
                    texto_pdf = ""
                    for pagina in leitor.pages:
                        texto = pagina.extract_text()
                        if texto:
                            texto_pdf += texto + "\n"
                    
                    if not texto_pdf.strip():
                        st.warning("Não foi possível extrair texto digital do PDF. Certifique-se de que não é uma imagem escaneada.")
                    
                    # 2. Chamar a API do Gemini para processar os dados de metrologia de forma analítica
                    client = genai.Client(api_key=api_key)
                    
                    # Prompt estruturado para extração precisa de dados industriais
                    prompt = f"""
                    Você é um especialista em garantia da qualidade industrial e metrologia.
                    Analise o texto extraído do desenho técnico abaixo.
                    Identifique com precisão todas as cotas lineares normais (cotas normais), tolerâncias de posição, especificações de componentes e dados do cliente (como Caterpillar ou HORSCH).
                    
                    Texto do desenho:
                    {texto_pdf}
                    
                    Retorne uma lista estruturada e detalhada contendo:
                    - Item/Cota
                    - Dimensão Nominal
                    - Tolerância Superior/Inferior
                    - Tipo de Característica (Cota Normal ou Posição)
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    resultado_ia = response.text
                    
                    # 3. Carregar o arquivo Excel na memória para manipulação segura
                    wb = openpyxl.load_workbook(modelo_file)
                    ws = wb.active
                    
                    # Exemplo de preenchimento: Salvando a resposta analítica da IA em uma célula de log ou iniciando o loop
                    # Nota: Mantenha as fórmulas originais e preencha as células de dados de acordo com seu padrão.
                    # Aqui inserimos um exemplo na célula A10 apenas para demonstrar o fluxo funcionando.
                    if "A10" in ws:
                        ws["A10"] = "Dados Processados pela IA"
                    
                    # Salvar o resultado final em um arquivo temporário para download
                    output_path = "relatorio_preenchido_temporario.xlsx"
                    wb.save(output_path)
                    
                    st.success("🎉 Relatório preenchido com sucesso!")
                    
                    # Exibir uma prévia do que a IA extraiu para conferência visual
                    with st.expander("🔍 Visualizar dados extraídos pela IA"):
                        st.write(resultado_ia)
                    
                    # 4. Botão para o usuário baixar o Excel pronto
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Baixar Relatório Preenchido (Excel)",
                            data=file,
                            file_name="relatorio_inspecao_final.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"Ocorreu um erro durante o processamento: {e}")