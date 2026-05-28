const unsplashArchitectureIds = [
    '1564013799919-ab600027fbb6',
    '1512917774080-9991f1c4c750',
    '1600596542815-ffad4c1539a9',
    '1605146769289-440113cc3d00',
    '1600585154340-be6161a56a0c',
    '1560185007-cde436f6a1d0',
    '1583608205776-bd35b59b08fc',
    '1600573472550-8090b5e0745e',
    '1560448204-e02f11c3d0e2',
    '1598924958632-81b718094eea',
    '1600047508140-bdcb74c7e794',
    '1558036117-15d91a9e87a2',
    '1582268611958-ebfd1652d925',
    '1598228723793-52759bba239c',
    '1560184897-ae75b07e1ada',
    '1600585154526-d3dfb0e1cd51',
    '1600047508054-84e3c34a5e72',
    '1600566752355-35792bedcfea',
    '1600585154363-e63c67fd6f0a',
    '1600585152915-d208bec867a3',
    '1600585153490-76fb20a32601',
    '1600566753190-17f0baa2a6c3',
    '1600047508189-055b4335eed7',
    '1560520660-beb1b6b80d81',
    '1600566753086-0c7e1a89e43f',
    '1600047508080-6b2cfd8deaa5',
    '1600047508118-5155356f667b',
    '1600566752222-35792bedcfeb',
    '1560062187-0c55d4b6ca3e',
    '1560185007-b0e89965482a',
    '1512917757316-ab84b6b6e2a7',
    '1600585152323-627371077e94',
    '1600047508024-57ca9f15596e',
    '1560184897-ae75b07e1bca',
    '1600047508215-24a4eeb497c6',
    '1599422314377-394b8e7a74f5',
    '1600047508073-a6ffa0cf59ac',
    '1600585153837-264a5f5f4a24',
    '1598924958631-81b718094eea',
    '1600047508054-84e3c34a5e73'
]

const fallbackHouseImages = [
    '/images/house1.jpg',
    '/images/house2.jpg',
    '/images/house3.jpg',
    '/images/house4.jpg'
]

export const getDefaultHouseImage = (seed = 0) => {
    const idx = seed > 0 ? seed % fallbackHouseImages.length : Math.floor(Math.random() * fallbackHouseImages.length)
    return fallbackHouseImages[idx]
}

export const getHouseImage = (images, index = 0, houseId = 0) => {
    if (images && images.length > index && images[index]) {
        return images[index]
    }
    return getDefaultHouseImage(houseId)
}

export const getRandomImage = (width = 800, height = 600, houseId = 0) => {
    const photoId = houseId > 0
        ? getArchitecturePhotoId(houseId)
        : unsplashArchitectureIds[Math.floor(Math.random() * unsplashArchitectureIds.length)]
    return `https://images.unsplash.com/photo-${photoId}?w=${width}&h=${height}&fit=crop`
}

const getArchitecturePhotoId = (seed) => {
    if (!seed || seed <= 0) {
        return unsplashArchitectureIds[Math.floor(Math.random() * unsplashArchitectureIds.length)]
    }
    return unsplashArchitectureIds[seed % unsplashArchitectureIds.length]
}
