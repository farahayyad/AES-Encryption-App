import streamlit as st
import pandas as pd
import io
import base64

st.set_page_config(page_title="AES Encryption & Key Expansion", 
                   page_icon="https://fiverr-res.cloudinary.com/t_profile_original,q_auto,f_auto/attachments/profile/photo/47c0a2bc1fd48209db0e2d02fb061b84-1691777419655/b7ff978a-abc5-4c81-8117-f8b28ad14d00.jpg")
st.markdown("""
    <style>
        .stButton>button {
            color: white;
            background-color: #fc5626;
        }
    </style>
    """, 
    unsafe_allow_html=True,
)









def main():
    # Title
    #st.image('https://fiverr-res.cloudinary.com/t_profile_original,q_auto,f_auto/attachments/profile/photo/47c0a2bc1fd48209db0e2d02fb061b84-1691777419655/b7ff978a-abc5-4c81-8117-f8b28ad14d00.jpg')
    st.markdown("<h1 style='color:#fc5626'>AES Encryption & Key Expansion</span>", unsafe_allow_html=True)
    st.markdown("<h7 style='color:#fc5626'>This application was developed wholly by Farah Ayyad</span>", unsafe_allow_html=True)

    with st.sidebar:
        st.title("Enter Information Here ")

        #shared_key = "Thats my Kung Fu"
        shared_key = st.text_input("Enter shared key", "")
        if shared_key:
            st.write(f"Shared Key: {shared_key}")

        #plain_text = "Two One Nine Two"
        plain_text = st.text_input("Enter plain text message", "")
        if plain_text:
            st.write(f"Plain Text: {plain_text}")
        
        submit_button = st.button("Submit")



    if submit_button:

        st.title("Your Input")

        # Convert to Hex:
        def Text2Hex(s):
            return s.encode("utf-8").hex()
        
       # Convert key to hex
        shared_key = Text2Hex(shared_key)
        shared_key_length = len(shared_key) * 4

        # Convert plain text to hex
        plain_text = Text2Hex(plain_text)
        plain_text_length = len(plain_text) * 4

        # Create a dictionary to hold data
        data = {
            "Hex format": [shared_key, plain_text],
            "Length": [f"{shared_key_length} bits", f"{plain_text_length} bits"]
        }

        # Convert the dictionary to a DataFrame for displaying as a table
        df = pd.DataFrame(data, index=['Shared key', 'Plaintext'])

        # Display the table
        st.table(df)



        if len(plain_text)*4 != 128 or len(shared_key)*4 != 128:
            st.error("The lengths should be 128 bits.")
        else:
            # Generate w0, w1, w2, w3:
            w0 = shared_key[0:8]
            w1 = shared_key[8:16]
            w2 = shared_key[16:24]
            w3 = shared_key[24:32]

            Ws = [w0, w1, w2, w3]

            with st.expander("The Ws"):
                # Create a dictionary with w labels and values
                data = {f"w{i}": Ws[i] for i in range(4)}
                # Convert the dictionary to a DataFrame for displaying as a table
                df = pd.DataFrame(data, index=["Value"]) # Using a single row dataframe
                # Display the table
                st.table(df)

            # G Function:
            def LS_1_Byte(s):
                new_s = s[2:] + s[0:2]
                return new_s
            
            s_box_aes = pd.read_csv("Files/AES_S_BOX.csv")

            def Substitute_S_Box(s):
                new_s = ""
                i = 0
                while i < 8:
                    row = int(s[i], 16)
                    i = i+1
                    col = int(s[i], 16)
                    new_s = new_s + s_box_aes.iloc[row][col]
                    i = i+1
                return new_s
            def Hex_XOR_8(s1, s2):
                return hex(int(s1, 16) ^ int(s2, 16))[2:].zfill(8)
            def XOR_With_RconJ(s, round_num):
                RcJ = ["01", "02", "04", "08", "10", "20", "40", "80", "1B", "36"]
                RconJ = RcJ[round_num - 1] + "00" + "00" + "00"
                
                xor_result = Hex_XOR_8(RconJ, s)
                return xor_result
            def G_Function(round_num, g_input):
                after_ls = LS_1_Byte(g_input)
                after_s_box = Substitute_S_Box(after_ls)
                after_xor = XOR_With_RconJ(after_s_box, round_num)
                
                return after_xor
            
            # Key Expansion:
            rounds = [1,2,3,4,5,6,7,8,9,10]
            Ws = [w0, w1, w2, w3]
            round_keys = [shared_key]

            for r in rounds:
                this_r_key = ""
                for i in range(4):
                    
                    current_generation = len(Ws) 
                    
                    if (current_generation % 4 == 0):
                        g_f_output = G_Function(r, Ws[-1])
                        new_w = Hex_XOR_8(g_f_output, Ws[-4])
                        
                        Ws.append(new_w)
                        this_r_key = this_r_key + new_w
                    else:
                        
                        new_w = Hex_XOR_8(Ws[-1], Ws[-4])
                        
                        Ws.append(new_w)
                        this_r_key = this_r_key + new_w
                        
                round_keys.append(this_r_key)
            
            with st.expander("Round Keys"):
                # Collect round numbers and corresponding keys
                round_nums = [f"Round #{i}" for i in range(11)]
                round_keys_values = [round_keys[i] for i in range(11)]

                # Convert the lists to a DataFrame for displaying as a table
                df = pd.DataFrame({
                    "Round #": round_nums,
                    "Round Key": round_keys_values
                })

                # Display the table
                st.table(df)


            # Encryption:
            # Add round key 0
            def Hex_XOR_32(s1, s2):
                return hex(int(s1, 16) ^ int(s2, 16))[2:].zfill(32)
            round_0_output = Hex_XOR_32(plain_text, round_keys[0])


            # 10 Rounds
            def Substitute_S_Box_32(s):
                new_s = ""
                i = 0
                while i < 32:
                    row = int(s[i], 16)
                    i = i+1
                    col = int(s[i], 16)
                    new_s = new_s + s_box_aes.iloc[row][col]
                    i = i+1
                return new_s
            def transform_s(s):
                index = 0
            
                
                transform_s_1 = s[index] + s[index+1] + s[index+8] + s[index+9] + s[index+16] + s[index+17] + s[index+24] + s[index+25]
                index = index + 2 
                transform_s_2 = s[index] + s[index+1] + s[index+8] + s[index+9] + s[index+16] + s[index+17] + s[index+24] + s[index+25]
                index = index + 2
                transform_s_3 = s[index] + s[index+1] + s[index+8] + s[index+9] + s[index+16] + s[index+17] + s[index+24] + s[index+25]
                index = index + 2
                transform_s_4 = s[index] + s[index+1] + s[index+8] + s[index+9] + s[index+16] + s[index+17] + s[index+24] + s[index+25]
                    
                transformed_s_matrix = [transform_s_1, transform_s_2, transform_s_3, transform_s_4]
                
                return transformed_s_matrix
            def LS_2_Byte(s):
                new_s = s[4:] + s[0:4]
                return new_s
            def LS_3_Byte(s):
                new_s = s[6:] + s[0:6]
                return new_s
            def shift_rows(s):
                transformed_s = transform_s(s)
                shifted_s_matrix = [[transformed_s[0]], [LS_1_Byte(transformed_s[1])], [LS_2_Byte(transformed_s[2])], [LS_3_Byte(transformed_s[3])]]
                return shifted_s_matrix

            def bitwise_left(s):
                s = s * 2
                return s

            def bitwise_xor(a, b):
                # convert a and b from decimal to bin 
                a = bin(a)[2:].zfill(32)
                b = bin(b)[2:].zfill(32)
                c = ""
                i = 0
                
                while i < 32:
                    if a[i] == b[i]:
                        c = c + "0"
                    else:
                        c = c + "1"
                    i = i + 1
                # convert to int
                c = int(c,2)
                return c

            def bitwise_and(a, b):
                # convert a and b from decimal to bin 
                a = bin(a)[2:].zfill(32)
                b = bin(b)[2:].zfill(32)
                c = ""
                i = 0
                
                while i < 32:
                    if a[i] == b[i]:
                        if a[i] == "1":
                            c = c+"1"
                        else:
                            c = c+"0"
                    else:
                        c = c+"0"
                    i = i +1
                c = int(c,2)
                return c

            def mpy(x, y):                  # mpy two 8 bit values

                x = int(x, 2)
                y = int(y, 2)
                
                p = 283             # mpy modulo x^8+x^4+x^3+x+1
                m = 0                       # m will be product
                
                for i in range(8):
                    m = bitwise_left(m)
                    
                    if bitwise_and(m, 256):
                        m = bitwise_xor(m, p)
                        
                    if bitwise_and(y, 128):
                        m = bitwise_xor(m, x)
                        
                    y = bitwise_left(y)
                return m
            def toColumns(s):
                new_s = []
                
                new_s.append(s[0][0][0:2] + s[1][0][0:2] + s[2][0][0:2] + s[3][0][0:2]) # first column
                new_s.append(s[0][0][2:4] + s[1][0][2:4] + s[2][0][2:4] + s[3][0][2:4]) # second column
                new_s.append(s[0][0][4:6] + s[1][0][4:6] + s[2][0][4:6] + s[3][0][4:6]) # third column
                new_s.append(s[0][0][6:8] + s[1][0][6:8] + s[2][0][6:8] + s[3][0][6:8]) # fourth column
                
                return new_s
            def Hex2Bin(word):
                bin_word = ""
                for i in word:
                    bin_word = bin_word + bin(int(i, 16))[2:].zfill(4)
                return bin_word
            def XOR(s1, s2):
                c = ""
                for i in range(8):
                    if s1[i] == s2[i]:
                        c = c + "0"
                    else:
                        c = c + "1"
                return c
            def Hex_Multiply(s1, s2):
                # s1 and s2 are in list --> must convert to string (hexadecimal)
                s1 = s1[0]

                x1 = mpy(Hex2Bin(s1[0:2]), Hex2Bin(s2[0:2]))
                x2 = mpy(Hex2Bin(s1[2:4]), Hex2Bin(s2[2:4]))
                x3 = mpy(Hex2Bin(s1[4:6]), Hex2Bin(s2[4:6]))
                x4 = mpy(Hex2Bin(s1[6:8]), Hex2Bin(s2[6:8]))

                # answers in decimal
                x1 = bin(x1)[2:].zfill(8)
                x2 = bin(x2)[2:].zfill(8)
                x3 = bin(x3)[2:].zfill(8)
                x4 = bin(x4)[2:].zfill(8)

                x5 = XOR(x1, x2)
                x6 = XOR(x3, x4)
                
                c = XOR(x5, x6)

                # bin to hex
                c = hex(int(c, 2))[2:].zfill(2)

                return c


            def mix_columns(s):
                s_columns = toColumns(s)
                fixed_matrix = [['02030101'], ['01020301'], ['01010203'], ['03010102']]
                
                mix_column_matrix = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]

                for r in range(4):
                    for c in range(4):
                        mix_column_matrix[r][c] = Hex_Multiply(fixed_matrix[r], s_columns[c])
                return mix_column_matrix
            def matrix2norm(s):
                new_s = ""
                for c in range(4):
                    for r in range(4):
                        new_s = new_s + s[r][c]
                return new_s
            def makeProperMatrix(s):
                my_m = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
                for r in range(4):
                    row = s[r][0]
                    my_m[r][0] = row[0:2]
                    my_m[r][1] = row[2:4]
                    my_m[r][2] = row[4:6]
                    my_m[r][3] = row[6:8]

                return my_m
            i = 1
            round_outputs = [round_0_output]
            round_input = round_0_output

            while i <= 10:
                # Substitue Bytes
                s_box_output = Substitute_S_Box_32(round_input)
                # Shift Rows
                shift_rows_output_matrix = shift_rows(s_box_output)
                # Mix Columns
                if i == 10:
                    mix_columns_output_matrix = makeProperMatrix(shift_rows_output_matrix) # it is not actually output of mix columns, just for naming purposes
                else:
                    mix_columns_output_matrix = mix_columns(shift_rows_output_matrix)
                # Add round key
                mix_columns_output_NORMAL = matrix2norm(mix_columns_output_matrix)
                add_round_key_output = Hex_XOR_32(mix_columns_output_NORMAL, round_keys[i])
                
                round_outputs.append(add_round_key_output)
                round_input = add_round_key_output

                i = i+1
            
            with st.expander("Round Outputs"):
                # Collect round numbers and corresponding outputs
                round_nums = [f"Round {index}" for index, _ in enumerate(round_outputs)]
                round_outputs_values = round_outputs

                # Convert the lists to a DataFrame for displaying as a table
                df = pd.DataFrame({
                    "Round #": round_nums,
                    "Round Output": round_outputs_values
                })

                # Display the table
                st.table(df)

            cipher_text = round_outputs[10]
            st.success(f"Cipher text is: {cipher_text}")




if __name__ == "__main__":
    main()
