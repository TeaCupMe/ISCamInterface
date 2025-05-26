from ISParser import ISParser
from serial import Serial
import time

CHUNK_SIZE = 240

class ISCamera:
    imageProperties = dict()
    def getProperties(self, ser: Serial) -> dict:
        ser.write(b'p')
        ser.read_until(b"\xFF\xFF\x00")
        st = ser.read_until(b"\x00\xFF\x00")
        self.imageProperties = ISParser.parseImageProperties(bytes(st)[:-3])
        return self.imageProperties
    
    def getImage(self, ser: Serial):
        ser.flush()
        ser.write(b'p')
        ser.read_until(b"\xFF\xFF\x00")
        self.getProperties(ser)
        # packetSize = imageProp["packetSize"]
        print("image data received")
        ser.write(b'r')
        print("chunk counter reset")
        time.sleep(0.1)
        
        with open("./data.txt", "wb") as file:
            file.write(bytes(f"{self.imageProperties['width']};{self.imageProperties['height']};{self.imageProperties['colorspace']}\n", encoding='ascii'))
        readStart = time.time()
        file = open("./data.txt", "ab")
        for i in range(self.imageProperties['numberOfChunks']):
            # ser.flush()
            ser.write(b'n')
            ser.flush()
            # print("next chunk request sent")
            ser.read_until(b"\xFF\xFF\x00")
            chunk = ISParser.parseImageChunk(ser.read(CHUNK_SIZE+6))
            print(chunk)
            file.write(bytes(chunk["payload"]))
            
            print(f'Chunk {chunk["chunkID"]} recieved!')
            # makeImage()
            if chunk['isLastChunk']!=0:
                print("Last chunk!")
                break
        file.close()
        print(f"Image received in {time.time() - readStart} seconds")
        
    def getNextChunk(self, ser: Serial) -> dict:
        ser.write(b'n')
        ser.flush()
        # print("next chunk request sent")
        ser.read_until(b"\xFF\xFF\x00")
        chunk = ISParser.parseImageChunk(ser.read(CHUNK_SIZE+6))
        # print(chunk)
        # file.write(bytes(chunk["payload"]))
        
        # print(f'Chunk {chunk["chunkID"]} recieved!')
        # makeImage()
        if chunk['isLastChunk']!=0:
            print("Last chunk!")
            
        return chunk
    def takeImage(self, ser: Serial):
        ser.write(b"t")
        ser.read_until(b"\xFF\xFF\x00\x00\xFF\x00")
        
    def setExposure(self, value: int, ser: Serial):
        ser.write(b'e')
        ser.write(value.to_bytes(2, 'little'))
        
    def setSize(self, width:int, height:int, ser: Serial):
        ser.write(b's')
        ser.write(width.to_bytes(2, 'little'))
        ser.write(height.to_bytes(2, 'little'))